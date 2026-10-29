package com.bizinsightiq.web;

import com.bizinsightiq.client.PythonMlClient;
import com.bizinsightiq.domain.model.User;
import com.bizinsightiq.domain.repository.UserRepository;
import com.bizinsightiq.security.JwtTokenProvider;
import com.bizinsightiq.security.UserPrincipal;
import com.bizinsightiq.web.dto.LoginRequest;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class AuthControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private JwtTokenProvider tokenProvider;

    @MockBean
    private PythonMlClient pythonMlClient;

    private User testUser;

    @BeforeEach
    void setUp() {
        userRepository.deleteAll();
        testUser = new User(
                "sarah_analyst",
                "sarah@bizinsightiq.com",
                passwordEncoder.encode("Password@123"),
                "ROLE_ANALYST"
        );
        testUser = userRepository.saveAndFlush(testUser);
    }

    @Test
    @DisplayName("POST /api/v1/auth/login should issue JWT when credentials are valid")
    void testLoginSuccess() throws Exception {
        LoginRequest request = new LoginRequest("sarah_analyst", "Password@123");

        mockMvc.perform(post("/api/v1/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.accessToken", not(emptyOrNullString())))
                .andExpect(jsonPath("$.tokenType", is("Bearer")))
                .andExpect(jsonPath("$.expiresIn", greaterThan(0)))
                .andExpect(jsonPath("$.user.id", is(testUser.getId().toString())))
                .andExpect(jsonPath("$.user.username", is("sarah_analyst")))
                .andExpect(jsonPath("$.user.email", is("sarah@bizinsightiq.com")))
                .andExpect(jsonPath("$.user.role", is("ROLE_ANALYST")))
                .andExpect(jsonPath("$.user.passwordHash").doesNotExist());
    }

    @Test
    @DisplayName("POST /api/v1/auth/login should reject incorrect password with generic 401")
    void testLoginWrongPassword() throws Exception {
        LoginRequest request = new LoginRequest("sarah_analyst", "WrongPassword999");

        mockMvc.perform(post("/api/v1/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.status", is(401)))
                .andExpect(jsonPath("$.error", is("Unauthorized")))
                .andExpect(jsonPath("$.message", is("Invalid username or password")));
    }

    @Test
    @DisplayName("POST /api/v1/auth/login should reject non-existent user with generic 401")
    void testLoginUnknownUsername() throws Exception {
        LoginRequest request = new LoginRequest("ghost_user", "SomePassword123");

        mockMvc.perform(post("/api/v1/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.status", is(401)))
                .andExpect(jsonPath("$.error", is("Unauthorized")))
                .andExpect(jsonPath("$.message", is("Invalid username or password")));
    }

    @Test
    @DisplayName("POST /api/v1/auth/login should reject blank request with 400 Bad Request")
    void testLoginValidationFailure() throws Exception {
        LoginRequest request = new LoginRequest("", "");

        mockMvc.perform(post("/api/v1/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.status", is(400)))
                .andExpect(jsonPath("$.validationErrors.username", notNullValue()))
                .andExpect(jsonPath("$.validationErrors.password", notNullValue()));
    }

    @Test
    @DisplayName("GET /api/v1/auth/me should return user profile when authenticated with valid JWT")
    void testGetCurrentUserSuccess() throws Exception {
        UserPrincipal principal = UserPrincipal.create(testUser);
        String token = tokenProvider.generateToken(principal);

        mockMvc.perform(get("/api/v1/auth/me")
                        .header("Authorization", "Bearer " + token))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id", is(testUser.getId().toString())))
                .andExpect(jsonPath("$.username", is("sarah_analyst")))
                .andExpect(jsonPath("$.email", is("sarah@bizinsightiq.com")))
                .andExpect(jsonPath("$.role", is("ROLE_ANALYST")))
                .andExpect(jsonPath("$.passwordHash").doesNotExist());
    }

    @Test
    @DisplayName("GET /api/v1/auth/me should return 401 when Authorization header is missing")
    void testGetCurrentUserMissingToken() throws Exception {
        mockMvc.perform(get("/api/v1/auth/me"))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.status", is(401)));
    }

    @Test
    @DisplayName("GET /api/v1/auth/me should return 401 when token is tampered")
    void testGetCurrentUserTamperedToken() throws Exception {
        UserPrincipal principal = UserPrincipal.create(testUser);
        String token = tokenProvider.generateToken(principal);
        String tampered = token.substring(0, token.length() - 4) + "zzzz";

        mockMvc.perform(get("/api/v1/auth/me")
                        .header("Authorization", "Bearer " + tampered))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.status", is(401)));
    }
}
