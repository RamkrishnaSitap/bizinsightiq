package com.bizinsightiq.web.controller;

import com.bizinsightiq.security.AuthService;
import com.bizinsightiq.security.UserPrincipal;
import com.bizinsightiq.web.dto.AuthResponse;
import com.bizinsightiq.web.dto.LoginRequest;
import com.bizinsightiq.web.dto.UserProfileResponse;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/auth")
public class AuthController {

    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@Valid @RequestBody LoginRequest request) {
        AuthResponse response = authService.login(request);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/me")
    public ResponseEntity<UserProfileResponse> getCurrentUser(@AuthenticationPrincipal UserPrincipal principal) {
        if (principal == null) {
            throw new AccessDeniedException("Full authentication required to view profile");
        }
        UserProfileResponse profile = authService.getCurrentUser(principal);
        return ResponseEntity.ok(profile);
    }
}
