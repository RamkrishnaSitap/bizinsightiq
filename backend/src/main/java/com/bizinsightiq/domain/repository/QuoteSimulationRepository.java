package com.bizinsightiq.domain.repository;

import com.bizinsightiq.domain.model.QuoteSimulation;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface QuoteSimulationRepository extends JpaRepository<QuoteSimulation, UUID> {
    List<QuoteSimulation> findByUserIdOrderByCreatedAtDesc(UUID userId);
    Page<QuoteSimulation> findByUserIdOrderByCreatedAtDesc(UUID userId, Pageable pageable);
    Optional<QuoteSimulation> findByIdAndUserId(UUID id, UUID userId);
}
