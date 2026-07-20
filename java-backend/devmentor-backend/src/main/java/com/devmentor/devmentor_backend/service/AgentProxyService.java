package com.devmentor.devmentor_backend.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

@Service
public class AgentProxyService {

    @Value("${fastapi.base.url}")
    private String fastApiBaseUrl;

    private final RestTemplate restTemplate = new RestTemplate();

    public Map<String, Object> callAgent(String endpoint, String message) {
        String url = fastApiBaseUrl + endpoint;

        Map<String, String> requestBody = new HashMap<>();
        requestBody.put("message", message);

        Map<String, Object> response = restTemplate.postForObject(url, requestBody, Map.class);

        return response;
    }
}