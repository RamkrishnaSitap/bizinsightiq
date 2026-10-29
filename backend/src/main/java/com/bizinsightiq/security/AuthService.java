package com.bizinsightiq.security;

import com.bizinsightiq.domain.model.User;
import com.bizinsightiq.domain.repository.UserRepository;
import com.bizinsightiq.web.dto.AuthResponse;
import com.bizinsightiq.web.dto.LoginRequest;
import com.bizinsightiq.web.dto.UserProfileResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AuthService {

    private static final Logger log = LoggerFactory.getLogger(AuthService.class);

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider tokenProvider;

    public AuthService(UserRepository userRepository,
                       PasswordEncoder passwordEncoder,
                       JwtTokenProvider tokenProvider) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.tokenProvider = tokenProvider;
    }

    @Transactional(readOnly = true)
    public AuthResponse login(LoginRequest request) {
        log.debug("Processing login attempt for username: {}", request.username());

        User user = userRepository.findByUsername(request.username())
                .orElseThrow(() -> {
                    log.warn("Login failed: username '{}' not found", request.username());
                    return new BadCredentialsException("Invalid username or password");
                });

        if (!passwordEncoder.matches(request.password(), user.getPasswordHash())) {
            log.warn("Login failed: password mismatch for username '{}'", request.username());
            throw new BadCredentialsException("Invalid username or password");
        }

        UserPrincipal principal = UserPrincipal.create(user);
        String jwt = tokenProvider.generateToken(principal);

        UserProfileResponse profile = new UserProfileResponse(
                user.getId(),
                user.getUsername(),
                user.getEmail(),
                user.getRole()
        );

        return new AuthResponse(jwt, tokenProvider.getJwtExpirationMs(), profile);
    }

    public UserProfileResponse getCurrentUser(UserPrincipal principal) {
        return new UserProfileResponse(
                principal.getId(),
                principal.getUsername(),
                principal.getEmail(),
                principal.getRole()
        );
    }
}
