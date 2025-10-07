package com.underwriting.domain;

public enum SubmissionStatus {
    NEW("New"),
    INTAKE("Intake"),
    IN_REVIEW("In Review"),
    ASSIGNED("Assigned"),
    QUOTED("Quoted"),
    BOUND("Bound"),
    DECLINED("Declined"),
    WITHDRAWN("Withdrawn"),
    COMPLETED("Completed");

    private final String displayName;

    SubmissionStatus(String displayName) {
        this.displayName = displayName;
    }

    public String getDisplayName() {
        return displayName;
    }

    @Override
    public String toString() {
        return displayName;
    }
}