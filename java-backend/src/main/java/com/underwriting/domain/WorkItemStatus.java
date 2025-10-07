package com.underwriting.domain;

public enum WorkItemStatus {
    PENDING("Pending"),
    IN_REVIEW("In Review"),
    APPROVED("Approved"),
    REJECTED("Rejected");

    private final String displayName;

    WorkItemStatus(String displayName) {
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

enum WorkItemPriority {
    LOW("Low"),
    MODERATE("Moderate"),
    MEDIUM("Medium"),
    HIGH("High"),
    CRITICAL("Critical");

    private final String displayName;

    WorkItemPriority(String displayName) {
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

enum CompanySize {
    SMALL("Small"),
    MEDIUM("Medium"),
    LARGE("Large"),
    ENTERPRISE("Enterprise");

    private final String displayName;

    CompanySize(String displayName) {
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