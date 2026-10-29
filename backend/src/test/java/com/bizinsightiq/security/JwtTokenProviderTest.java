package com.bizinsightiq.security;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.security.core.authority.SimpleGrantedAuthority;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.List;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

class JwtTokenProviderTest {

    private static final String TEST_SECRET = "BizInsightIQTestSecretKeyForJwtAuthenticationMustBeAtLeast256BitsLong2026!";
    private static final long EXPIRATION_MS = 3600000; // 1 hour

    private JwtTokenProvider tokenProvider;
    private UserPrincipal testPrincipal;
    private UUID testUserId;

    @BeforeEach
    void setUp() {
        tokenProvider = new JwtTokenProvider(TEST_SECRET, EXPIRATION_MS);
        testUserId = UUID.randomUUID();
        testPrincipal = new UserPrincipal(
                testUserId,
                "analyst_john",
                "john@bizinsightiq.com",
                "$2a$10$hashedpassword",
                "ROLE_ANALYST",
                List.of(new SimpleGrantedAuthority("ROLE_ANALYST"))
        );
    }

    @Test
    @DisplayName("generateToken and validateToken should succeed for valid user principal")
    void testTokenGenerationAndValidation() {
        String token = tokenProvider.generateToken(testPrincipal);
        assertNotNull(token);
        assertTrue(tokenProvider.validateToken(token));

        assertEquals(testUserId, tokenProvider.getUserIdFromToken(token));
        assertEquals("analyst_john", tokenProvider.getUsernameFromToken(token));
        assertEquals("ROLE_ANALYST", tokenProvider.getRoleFromToken(token));
    }

    @Test
    @DisplayName("validateToken should reject malformed token strings")
    void testMalformedTokenRejected() {
        assertFalse(tokenProvider.validateToken("not-a-valid-jwt-token"));
        assertFalse(tokenProvider.validateToken("header.payload"));
        assertFalse(tokenProvider.validateToken(""));
        assertFalse(tokenProvider.validateToken(null));
    }

    @Test
    @DisplayName("validateToken should reject tampered tokens")
    void testTamperedTokenRejected() {
        String validToken = tokenProvider.generateToken(testPrincipal);
        // Tamper with the signature portion
        String tamperedToken = validToken.substring(0, validToken.length() - 5) + "abcde";
        assertFalse(tokenProvider.validateToken(tamperedToken));
    }

    @Test
    @DisplayName("validateToken should reject expired tokens")
    void testExpiredTokenRejected() {
        SecretKey key = Keys.hmacShaKeyFor(TEST_SECRET.getBytes(StandardCharsets.UTF_8));
        Date past = new Date(System.currentTimeMillis() - 10000); // 10s in the past
        String expiredToken = Jwts.builder()
                .subject(testUserId.toString())
                .claim("username", "expired_user")
                .claim("role", "ROLE_ANALYST")
                .issuedAt(new Date(past.getTime() - 10000))
                .expiration(past)
                .signWith(key, Jwts.SIG.HS256)
                .compact();

        assertFalse(tokenProvider.validateToken(expiredToken));
    }

    @Test
    @DisplayName("validateToken should reject tokens signed with a different key")
    void testDifferentSigningKeyRejected() {
        String differentSecret = "AnotherCompletelyDifferentSecretKeyThatHasMoreThan256BitsForTestingPurposes12345!";
        JwtTokenProvider otherProvider = new JwtTokenProvider(differentSecret, EXPIRATION_MS);

        String foreignToken = otherProvider.generateToken(testPrincipal);
        assertFalse(tokenProvider.validateToken(foreignToken));
    }

    @Test
    @DisplayName("Constructor should fail safely if secret key is shorter than 256 bits")
    void testShortSecretRejected() {
        assertThrows(IllegalArgumentException.class, () -> new JwtTokenProvider("too-short-secret", EXPIRATION_MS));
        assertThrows(IllegalStateException.class, () -> new JwtTokenProvider("", EXPIRATION_MS));
        assertThrows(IllegalStateException.class, () -> new JwtTokenProvider(null, EXPIRATION_MS));
    }
}
