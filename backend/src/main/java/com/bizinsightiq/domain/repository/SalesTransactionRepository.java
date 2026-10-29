package com.bizinsightiq.domain.repository;

import com.bizinsightiq.domain.model.SalesTransaction;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface SalesTransactionRepository extends JpaRepository<SalesTransaction, Long> {
    List<SalesTransaction> findByDatasetId(UUID datasetId);
    Page<SalesTransaction> findByDatasetId(UUID datasetId, Pageable pageable);
    long countByDatasetId(UUID datasetId);
    void deleteByDatasetId(UUID datasetId);
}
