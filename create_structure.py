import os

directories_and_files = {
    "gateway-service": [
        "Dockerfile",
        "requirements.txt",
        "pyproject.toml",
        "app/__init__.py",
        "app/main.py",
        "app/api/v1/__init__.py",
        "app/api/v1/router.py",
        "app/api/v1/auth.py",
        "app/api/v1/scan.py",
        "app/api/v1/neutralize.py",
        "app/api/v1/reports.py",
        "app/api/v1/admin.py",
        "app/api/v1/health.py",
        "app/core/__init__.py",
        "app/core/config.py",
        "app/core/security.py",
        "app/core/rate_limiter.py",
        "app/core/exceptions.py",
        "app/middleware/__init__.py",
        "app/middleware/cors.py",
        "app/middleware/logging.py",
        "app/middleware/tracing.py",
        "app/middleware/input_validation.py",
        "app/models/__init__.py",
        "app/models/user.py",
        "app/models/token.py",
        "app/models/api_key.py",
        "app/schemas/__init__.py",
        "app/schemas/auth.py",
        "app/schemas/scan.py",
        "app/schemas/common.py",
        "app/services/__init__.py",
        "app/services/auth_service.py",
        "app/services/proxy_service.py"
    ],
    "image-analysis-service": [
        "Dockerfile",
        "requirements.txt",
        "pyproject.toml",
        "app/__init__.py",
        "app/main.py",
        "app/api/__init__.py",
        "app/api/analyze.py",
        "app/api/batch.py",
        "app/api/health.py",
        "app/engines/__init__.py",
        "app/engines/base.py",
        "app/engines/chi_square.py",
        "app/engines/rs_analysis.py",
        "app/engines/spa_analysis.py",
        "app/engines/visual_attack.py",
        "app/engines/dct_analysis.py",
        "app/features/__init__.py",
        "app/features/spatial.py",
        "app/features/frequency.py",
        "app/features/statistical.py",
        "app/features/rich_model.py",
        "app/classifiers/__init__.py",
        "app/classifiers/base.py",
        "app/classifiers/cnn_clf.py",
        "app/classifiers/ensemble.py",
        "app/classifiers/xgboost_clf.py",
        "app/classifiers/svm_clf.py",
        "app/yara_rules/stego_signatures.yar",
        "app/yara_rules/payload_patterns.yar",
        "app/yara_rules/custom/.gitkeep", # To keep empty dir
        "app/utils/__init__.py",
        "app/utils/image_loader.py",
        "app/utils/feature_cache.py",
        "app/schemas/__init__.py",
        "app/schemas/analysis_request.py",
        "app/schemas/analysis_response.py",
        "app/models/__init__.py",
        "app/models/scan_result.py",
        "ml_models/cnn_steg_detector.h5", # Placeholder
        "ml_models/ensemble_v1.pkl", # Placeholder
        "ml_models/xgboost_stacker_v1.pkl", # Placeholder
        "training/train_cnn.py",
        "training/train_ensemble.py",
        "training/calibrate_thresholds.py",
        "training/evaluate_all.py",
        "tests/conftest.py",
        "tests/test_chi_square.py",
        "tests/test_rs_analysis.py",
        "tests/test_cnn_classifier.py",
        "tests/test_ensemble.py",
        "tests/fixtures/clean_sample.png", # Placeholder
        "tests/fixtures/stego_sample.png" # Placeholder
    ],
    "dnn-defense-service": [
        "Dockerfile",
        "requirements.txt",
        "app/__init__.py",
        "app/main.py",
        "app/api/__init__.py",
        "app/api/analyze_model.py",
        "app/api/compare_models.py",
        "app/api/health.py",
        "app/parsers/__init__.py",
        "app/parsers/base_parser.py",
        "app/parsers/tensorflow_parser.py",
        "app/parsers/pytorch_parser.py",
        "app/parsers/onnx_parser.py",
        "app/parsers/safetensors_parser.py",
        "app/analyzers/__init__.py",
        "app/analyzers/weight_distribution.py",
        "app/analyzers/anomaly_detector.py",
        "app/analyzers/gradient_inspector.py",
        "app/analyzers/layer_comparator.py",
        "app/analyzers/capacity_estimator.py",
        "app/schemas/__init__.py",
        "app/schemas/model_request.py",
        "app/schemas/model_response.py",
        "app/utils/__init__.py",
        "app/utils/model_loader.py"
    ],
     "neutralization-service": [
        "Dockerfile",
        "requirements.txt",
        "app/__init__.py",
        "app/main.py",
        "app/api/__init__.py",
        "app/api/neutralize.py",
        "app/api/batch_neutralize.py",
        "app/api/preview.py",
        "app/api/verify.py",
        "app/api/health.py",
        "app/strategies/__init__.py",
        "app/strategies/base_strategy.py",
        "app/strategies/lsb_scrubber.py",
        "app/strategies/dct_reencoder.py",
        "app/strategies/pixel_jitter.py",
        "app/strategies/metadata_stripper.py",
        "app/strategies/format_converter.py",
        "app/strategies/dnn_weight_pruner.py",
        "app/strategies/composite_strategy.py",
        "app/selector/__init__.py",
        "app/selector/strategy_selector.py",
        "app/selector/strategy_registry.py",
        "app/integrity/__init__.py",
        "app/integrity/ssim_checker.py"
     ],
     "orchestration-service": [
        "Dockerfile",
        "requirements.txt",
         "app/__init__.py",
         "app/main.py",
         "app/worker.py",
         "app/tasks.py"
     ],
     "notification-service": [
         "Dockerfile",
         "requirements.txt",
         "app/__init__.py",
         "app/main.py",
         "app/websockets.py"
     ],
     "docker/nginx/ssl": [
         ".gitkeep"
     ]
}

def create_structure():
    base_dir = r"c:\stego-hunter"
    os.chdir(base_dir)

    for service_name, files in directories_and_files.items():
        if not os.path.exists(service_name):
            os.makedirs(service_name)
        
        for file_path in files:
            full_path = os.path.join(service_name, file_path)
            directory = os.path.dirname(full_path)
            
            # Create directories if they don't exist
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # Create empty files
            if not os.path.exists(full_path):
                with open(full_path, 'w') as f:
                    pass

    # Create root docker files
    if not os.path.exists("docker/nginx/nginx.conf"):
        os.makedirs("docker/nginx", exist_ok=True)
        with open("docker/nginx/nginx.conf", 'w') as f:
            pass
    
    with open("docker/docker-compose.yml", 'w') as f:
            pass
    with open("docker/docker-compose.prod.yml", 'w') as f:
            pass
    with open("docker/docker-compose.monitoring.yml", 'w') as f:
            pass

    print("Directory structure created successfully.")

if __name__ == "__main__":
    create_structure()
