package com.islanddelta.config;

import com.islanddelta.common.PasswordUtil;
import com.islanddelta.domain.Admin;
import com.islanddelta.repository.AdminRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class DataInitConfig {

    private static final Logger log = LoggerFactory.getLogger(DataInitConfig.class);

    @Bean
    CommandLineRunner initAdmin(AdminRepository adminRepository) {
        return args -> {
            if (adminRepository.count() == 0) {
                Admin admin = new Admin();
                admin.setUsername("admin");
                admin.setPasswordHash(PasswordUtil.hash("admin123"));
                admin.setRole("admin");
                admin.setStatus("normal");
                adminRepository.save(admin);
                log.info("Default admin created: username=admin, password=admin123");
            }
        };
    }
}
