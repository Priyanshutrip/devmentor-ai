package com.devmentor.devmentor_backend.controller;

import com.devmentor.devmentor_backend.dto.TaskRequest;
import com.devmentor.devmentor_backend.service.AgentProxyService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/agent")
public class AgentController {

    @Autowired
    private AgentProxyService agentProxyService;

    @PostMapping("/ask")
    public Map<String, Object> ask(@RequestBody TaskRequest request) {
        return agentProxyService.callAgent("/ask", request.getMessage());
    }

    @PostMapping("/review")
    public Map<String, Object> review(@RequestBody TaskRequest request) {
        return agentProxyService.callAgent("/review", request.getMessage());
    }

    @PostMapping("/plan")
    public Map<String, Object> plan(@RequestBody TaskRequest request) {
        return agentProxyService.callAgent("/plan", request.getMessage());
    }

    @PostMapping("/orchestrate")
    public Map<String, Object> orchestrate(@RequestBody TaskRequest request) {
        return agentProxyService.callAgent("/orchestrate", request.getMessage());
    }
}