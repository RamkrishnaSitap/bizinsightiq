package com.bizinsightiq.domain.repository;

import com.bizinsightiq.domain.model.CustomerCluster;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface CustomerClusterRepository extends JpaRepository<CustomerCluster, Long> {
    List<CustomerCluster> findBySegmentationRunId(UUID segmentationRunId);
    Optional<CustomerCluster> findBySegmentationRunIdAndCustomerId(UUID segmentationRunId, String customerId);
    List<CustomerCluster> findBySegmentationRunIdAndClusterId(UUID segmentationRunId, Integer clusterId);
}
