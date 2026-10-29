package com.bizinsightiq.client.exception;

/**
 * Exception thrown when communication with the Python FastAPI microservice fails.
 */
public class FastApiException extends RuntimeException {

    private final int statusCode;

    public FastApiException(String message) {
        super(message);
        this.statusCode = 502; // Bad Gateway default
    }

    public FastApiException(String message, Throwable cause) {
        super(message, cause);
        this.statusCode = 502;
    }

    public FastApiException(String message, int statusCode) {
        super(message);
        this.statusCode = statusCode;
    }

    public int getStatusCode() {
        return statusCode;
    }
}
