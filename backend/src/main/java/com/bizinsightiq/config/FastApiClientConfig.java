package com.bizinsightiq.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestClient;

import java.time.Duration;

@Configuration
public class FastApiClientConfig {

    @Value("${app.fastapi.base-url:http://127.0.0.1:8000/api/v1}")
    private String fastApiBaseUrl;

    @Value("${app.fastapi.connect-timeout-ms:5000}")
    private int connectTimeoutMs;

    @Value("${app.fastapi.read-timeout-ms:15000}")
    private int readTimeoutMs;

    @Bean
    public RestClient fastApiRestClient(RestClient.Builder builder) {
        SimpleClientHttpRequestFactory requestFactory = new SimpleClientHttpRequestFactory();
        requestFactory.setConnectTimeout(Duration.ofMillis(connectTimeoutMs));
        requestFactory.setReadTimeout(Duration.ofMillis(readTimeoutMs));

        return builder
                .baseUrl(fastApiBaseUrl)
                .requestFactory(requestFactory)
                .build();
    }
}
