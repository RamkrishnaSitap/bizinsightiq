package com.bizinsightiq.domain.repository;

import com.bizinsightiq.domain.model.SegmentationRun;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface SegmentationRunRepository extends JpaRepository<SegmentationRun, UUID> {
    List<SegmentationRun> findByDatasetId(UUID datasetId);
    Optional<SegmentationRun> findTopByDatasetIdOrderByCreatedAtDesc(UUID datasetId);
}
