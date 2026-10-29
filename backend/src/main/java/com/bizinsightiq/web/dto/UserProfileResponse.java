package com.bizinsightiq.web.dto;

import java.util.UUID;

public record UserProfileResponse(
    UUID id,
    String username,
    String email,
    String role
) {}
