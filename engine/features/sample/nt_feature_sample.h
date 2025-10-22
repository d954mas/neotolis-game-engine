#ifndef NT_FEATURE_SAMPLE_H
#define NT_FEATURE_SAMPLE_H

typedef enum nt_feature_sample_status {
    NT_FEATURE_SAMPLE_STATUS_OK = 0,
    NT_FEATURE_SAMPLE_STATUS_DISABLED = 1
} nt_feature_sample_status;

typedef struct nt_feature_sample_config {
    int enabled;
} nt_feature_sample_config;

nt_feature_sample_status nt_feature_sample_init(const nt_feature_sample_config *config);
void nt_feature_sample_shutdown(void);

#endif // NT_FEATURE_SAMPLE_H
