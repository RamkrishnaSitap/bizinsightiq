package com.bizinsightiq;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

@SpringBootTest
@ActiveProfiles("test")
class BizInsightIqApplicationTests {

    @Test
    void contextLoads() {
        // Verifies Spring ApplicationContext starts cleanly with all beans resolved
    }
}
