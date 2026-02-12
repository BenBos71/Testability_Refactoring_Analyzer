# CI/CD Integration Examples

This document provides examples for integrating the Testability Analyzer into various CI/CD pipelines.

## Table of Contents

- [GitHub Actions](#github-actions)
- [GitLab CI](#gitlab-ci)
- [Jenkins](#jenkins)
- [Azure Pipelines](#azure-pipelines)
- [CircleCI](#circleci)
- [Quality Gates](#quality-gates)
- [Advanced Configurations](#advanced-configurations)

---

## GitHub Actions

### Basic Setup

```yaml
name: Testability Analysis
on: [push, pull_request]

jobs:
  testability:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'
    
    - name: Install testability analyzer
      run: pip install testability-analyzer
    
    - name: Run testability analysis
      run: |
        testability-analyzer src/ --output json > testability_results.json
    
    - name: Upload results
      uses: actions/upload-artifact@v3
      with:
        name: testability-results
        path: testability_results.json
```

### With Quality Gate

```yaml
name: Testability Analysis with Quality Gate
on: [push, pull_request]

jobs:
  testability:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'
    
    - name: Install dependencies
      run: |
        pip install testability-analyzer jq
    
    - name: Run testability analysis
      run: |
        testability-analyzer src/ --output json > testability_results.json
    
    - name: Check quality gate
      run: |
        avg_score=$(jq -r '.summary.score_statistics.average' testability_results.json)
        min_score=${MIN_SCORE:-70}
        
        echo "Average testability score: $avg_score"
        echo "Minimum required score: $min_score"
        
        if (( $(echo "$avg_score < $min_score" | bc -l) )); then
          echo "❌ Testability score ($avg_score) is below threshold ($min_score)"
          echo "Please improve code testability before merging."
          exit 1
        else
          echo "✅ Testability score ($avg_score) meets requirements"
        fi
    
    - name: Generate report
      if: always()
      run: |
        testability-analyzer src/ --verbose > testability_report.txt
    
    - name: Upload artifacts
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: testability-artifacts
        path: |
          testability_results.json
          testability_report.txt
```

### Multi-Project Setup

```yaml
name: Testability Analysis
on: [push, pull_request]

jobs:
  testability:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        project: [frontend, backend, shared]
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'
    
    - name: Install testability analyzer
      run: pip install testability-analyzer
    
    - name: Analyze ${{ matrix.project }}
      run: |
        testability-analyzer ${{ matrix.project }}/ --output json > ${{ matrix.project }}_results.json
    
    - name: Check quality gate for ${{ matrix.project }}
      run: |
        avg_score=$(jq -r '.summary.score_statistics.average' ${{ matrix.project }}_results.json)
        echo "${{ matrix.project }} score: $avg_score"
        
        if (( $(echo "$avg_score < 70" | bc -l) )); then
          echo "❌ ${{ matrix.project }} fails quality gate"
          exit 1
        fi
```

### Scheduled Analysis

```yaml
name: Weekly Testability Report
on:
  schedule:
    - cron: '0 6 * * 1'  # Every Monday at 6 AM UTC
  workflow_dispatch:

jobs:
  weekly_report:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'
    
    - name: Install testability analyzer
      run: pip install testability-analyzer
    
    - name: Generate weekly report
      run: |
        testability-analyzer src/ --output json --verbose > weekly_report.json
        testability-analyzer src/ --verbose > weekly_report.txt
    
    - name: Create summary
      run: |
        avg_score=$(jq -r '.summary.score_statistics.average' weekly_report.json)
        total_files=$(jq -r '.summary.total_files' weekly_report.json)
        red_flags=$(jq -r '.summary.total_red_flags' weekly_report.json)
        
        echo "# Weekly Testability Report" > summary.md
        echo "" >> summary.md
        echo "- Average Score: $avg_score" >> summary.md
        echo "- Total Files: $total_files" >> summary.md
        echo "- Red Flags: $red_flags" >> summary.md
        echo "" >> summary.md
        echo "## Detailed Report" >> summary.md
        echo "See attached artifacts for full analysis." >> summary.md
    
    - name: Create Issue for Low Scores
      if: failure()
      uses: actions/github-script@v6
      with:
        script: |
          github.rest.issues.create({
            owner: context.repo.owner,
            repo: context.repo.repo,
            title: 'Testability Score Below Threshold',
            body: 'The weekly testability analysis shows scores below the acceptable threshold. Please review the attached report and take corrective actions.',
            labels: ['testability', 'quality-gate']
          })
```

---

## GitLab CI

### Basic Configuration

```yaml
# .gitlab-ci.yml

stages:
  - test
  - quality

testability_analysis:
  stage: test
  image: python:3.8
  script:
    - pip install testability-analyzer
    - testability-analyzer src/ --output json > testability_results.json
  artifacts:
    reports:
      junit: testability_results.json
    paths:
      - testability_results.json
    expire_in: 1 week
  only:
    - merge_requests
    - main

testability_quality_gate:
  stage: quality
  image: python:3.8
  script:
    - pip install testability-analyzer jq
    - testability-analyzer src/ --output json > testability_results.json
    - avg_score=$(jq -r '.summary.score_statistics.average' testability_results.json)
    - min_score=${MIN_SCORE:-70}
    - |
      if (( $(echo "$avg_score < $min_score" | bc -l) )); then
        echo "❌ Testability score ($avg_score) is below threshold ($min_score)"
        exit 1
      else
        echo "✅ Testability score ($avg_score) meets requirements"
      fi
  dependencies:
    - testability_analysis
  only:
    - merge_requests
    - main
```

### Advanced GitLab CI

```yaml
# .gitlab-ci.yml

variables:
  TESTABILITY_MIN_SCORE: "70"

stages:
  - test
  - quality
  - report

testability:
  stage: test
  image: python:3.8
  before_script:
    - pip install testability-analyzer
  script:
    - mkdir -p testability-reports
    - |
      for dir in src/ tests/ tools/; do
        if [ -d "$dir" ]; then
          echo "Analyzing $dir..."
          testability-analyzer "$dir" --output json > "testability-reports/$(basename $dir).json"
          testability-analyzer "$dir" --verbose > "testability-reports/$(basename $dir).txt"
        fi
      done
  artifacts:
    reports:
      junit: testability-reports/*.json
    paths:
      - testability-reports/
    expire_in: 1 week
  coverage: '/Average score: \d+\.\d+/'
  only:
    - merge_requests
    - main

testability_quality_gate:
  stage: quality
  image: python:3.8
  before_script:
    - pip install testability-analyzer jq
  script:
    - |
      failed=false
      for report in testability-reports/*.json; do
        if [ -f "$report" ]; then
          avg_score=$(jq -r '.summary.score_statistics.average' "$report")
          dir_name=$(basename "$report" .json)
          echo "$dir_name score: $avg_score"
          
          if (( $(echo "$avg_score < $TESTABILITY_MIN_SCORE" | bc -l) )); then
            echo "❌ $dir_name fails quality gate"
            failed=true
          else
            echo "✅ $dir_name passes quality gate"
          fi
        fi
      done
      
      if [ "$failed" = true ]; then
        echo "One or more directories failed quality gate"
        exit 1
      fi
  dependencies:
    - testability
  only:
    - merge_requests
    - main

testability_report:
  stage: report
  image: python:3.8
  before_script:
    - pip install testability-analyzer jq
  script:
    - |
      echo "# Testability Analysis Report" > report.md
      echo "" >> report.md
      echo "Generated on: $(date)" >> report.md
      echo "" >> report.md
      echo "## Summary" >> report.md
      echo "" >> report.md
      
      total_files=0
      total_functions=0
      total_red_flags=0
      total_score=0
      dir_count=0
      
      for report in testability-reports/*.json; do
        if [ -f "$report" ]; then
          dir_name=$(basename "$report" .json)
          files=$(jq -r '.summary.total_files' "$report")
          functions=$(jq -r '.summary.total_functions' "$report")
          red_flags=$(jq -r '.summary.total_red_flags' "$report")
          avg_score=$(jq -r '.summary.score_statistics.average' "$report")
          
          echo "### $dir_name" >> report.md
          echo "- Files: $files" >> report.md
          echo "- Functions: $functions" >> report.md
          echo "- Red Flags: $red_flags" >> report.md
          echo "- Average Score: $avg_score" >> report.md
          echo "" >> report.md
          
          total_files=$((total_files + files))
          total_functions=$((total_functions + functions))
          total_red_flags=$((total_red_flags + red_flags))
          total_score=$(echo "$total_score + $avg_score" | bc)
          dir_count=$((dir_count + 1))
        fi
      done
      
      if [ $dir_count -gt 0 ]; then
        overall_avg=$(echo "scale=2; $total_score / $dir_count" | bc)
        echo "## Overall Summary" >> report.md
        echo "- Total Files: $total_files" >> report.md
        echo "- Total Functions: $total_functions" >> report.md
        echo "- Total Red Flags: $total_red_flags" >> report.md
        echo "- Overall Average Score: $overall_avg" >> report.md
      fi
  artifacts:
    paths:
      - report.md
    expire_in: 1 month
  dependencies:
    - testability
  only:
    - main
```

---

## Jenkins

### Jenkinsfile

```groovy
pipeline {
    agent any
    
    environment {
        MIN_SCORE = '70'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Python') {
            steps {
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate && pip install testability-analyzer'
            }
        }
        
        stage('Testability Analysis') {
            steps {
                sh '''
                    . venv/bin/activate
                    testability-analyzer src/ --output json > testability_results.json
                    testability-analyzer src/ --verbose > testability_report.txt
                '''
            }
            
            post {
                always {
                    archiveArtifacts artifacts: 'testability_results.json,testability_report.txt', fingerprint: true
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: '.',
                        reportFiles: 'testability_report.txt',
                        reportName: 'Testability Report',
                        reportTitles: 'Testability Analysis Report'
                    ])
                }
            }
        }
        
        stage('Quality Gate') {
            steps {
                sh '''
                    . venv/bin/activate
                    pip install jq
                    avg_score=$(jq -r '.summary.score_statistics.average' testability_results.json)
                    echo "Average testability score: $avg_score"
                    echo "Minimum required score: $MIN_SCORE"
                    
                    if (( $(echo "$avg_score < $MIN_SCORE" | bc -l) )); then
                        echo "❌ Testability score ($avg_score) is below threshold ($MIN_SCORE)"
                        exit 1
                    else
                        echo "✅ Testability score ($avg_score) meets requirements"
                    fi
                '''
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}
```

---

## Azure Pipelines

### azure-pipelines.yml

```yaml
trigger:
  branches:
    include:
      - main
  pull_request:
    branches:
      - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  minScore: 70

stages:
- stage: Testability
  jobs:
  - job: Analyze
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '3.8'
      displayName: 'Set up Python'

    - script: |
        pip install testability-analyzer
      displayName: 'Install testability analyzer'

    - script: |
        testability-analyzer src/ --output json > testability_results.json
        testability-analyzer src/ --verbose > testability_report.txt
      displayName: 'Run testability analysis'

    - script: |
        pip install jq
        avg_score=$(jq -r '.summary.score_statistics.average' testability_results.json)
        echo "Average testability score: $avg_score"
        echo "##vso[task.setvariable variable=score]$avg_score"
        
        if (( $(echo "$avg_score < $(minScore)" | bc -l) )); then
          echo "❌ Testability score ($avg_score) is below threshold ($(minScore))"
          exit 1
        else
          echo "✅ Testability score ($avg_score) meets requirements"
        fi
      displayName: 'Check quality gate'

    - publish: testability_results.json
      artifact: testability-results
      displayName: 'Publish JSON results'

    - publish: testability_report.txt
      artifact: testability-report
      displayName: 'Publish text report'

    - task: PublishTestResults@2
      condition: always()
      inputs:
        testResultsFiles: 'testability_results.json'
        testRunTitle: 'Testability Analysis'
      displayName: 'Publish test results'
```

---

## CircleCI

### .circleci/config.yml

```yaml
version: 2.1

orbs:
  python: circleci/python@2.0

jobs:
  testability-analysis:
    executor: python/default
    steps:
      - checkout
      - python/install-packages:
          pkg-manager: pip
          packages: |
            testability-analyzer
            jq
      
      - run:
          name: Run testability analysis
          command: |
            testability-analyzer src/ --output json > testability_results.json
            testability-analyzer src/ --verbose > testability_report.txt
      
      - run:
          name: Check quality gate
          command: |
            avg_score=$(jq -r '.summary.score_statistics.average' testability_results.json)
            min_score=${MIN_SCORE:-70}
            
            echo "Average testability score: $avg_score"
            echo "Minimum required score: $min_score"
            
            if (( $(echo "$avg_score < $min_score" | bc -l) )); then
              echo "❌ Testability score ($avg_score) is below threshold ($min_score)"
              exit 1
            else
              echo "✅ Testability score ($avg_score) meets requirements"
            fi
      
      - store_artifacts:
          path: testability_results.json
          destination: testability-results
      
      - store_artifacts:
          path: testability_report.txt
          destination: testability-report
      
      - store_test_results:
          path: testability_results.json

workflows:
  testability:
    jobs:
      - testability-analysis
```

---

## Quality Gates

### Score Thresholds

Recommended minimum scores for different environments:

```bash
# Production code
MIN_SCORE=80

# Development code
MIN_SCORE=70

# Experimental code
MIN_SCORE=60

# Critical systems
MIN_SCORE=85
```

### Multi-Level Quality Gates

```bash
#!/bin/bash
# quality_gate.sh

avg_score=$1
min_score=$2
warning_score=$3

echo "Score: $avg_score"
echo "Warning threshold: $warning_score"
echo "Failure threshold: $min_score"

if (( $(echo "$avg_score < $min_score" | bc -l) )); then
    echo "❌ FAIL: Score below minimum threshold"
    exit 1
elif (( $(echo "$avg_score < $warning_score" | bc -l) )); then
    echo "⚠️  WARNING: Score below warning threshold"
    exit 0
else
    echo "✅ PASS: Score meets requirements"
    exit 0
fi
```

### Trend Analysis

```bash
#!/bin/bash
# trend_analysis.sh

current_score=$1
history_file="score_history.txt"

# Read previous scores
if [ -f "$history_file" ]; then
    previous_score=$(tail -1 "$history_file")
    change=$(echo "$current_score - $previous_score" | bc)
    
    echo "Previous score: $previous_score"
    echo "Current score: $current_score"
    echo "Change: $change"
    
    if (( $(echo "$change < -5" | bc -l) )); then
        echo "📉 Score decreased significantly"
        exit 1
    elif (( $(echo "$change > 5" | bc -l) )); then
        echo "📈 Score improved significantly"
    fi
fi

# Save current score
echo "$current_score" >> "$history_file"
```

---

## Advanced Configurations

### Docker Integration

```dockerfile
FROM python:3.8-slim

# Install testability analyzer
RUN pip install testability-analyzer

# Create analysis script
COPY analyze.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/analyze.sh

ENTRYPOINT ["analyze.sh"]
```

```bash
#!/bin/bash
# analyze.sh

directory=${1:-src/}
output_format=${2:-text}
min_score=${3:-70}

echo "Analyzing directory: $directory"
echo "Output format: $output_format"
echo "Minimum score: $min_score"

# Run analysis
testability-analyzer "$directory" --output "$output_format" > results.txt

# Check quality gate if JSON output
if [ "$output_format" = "json" ]; then
    pip install jq
    avg_score=$(jq -r '.summary.score_statistics.average' results.txt)
    
    if (( $(echo "$avg_score < $min_score" | bc -l) )); then
        echo "❌ Quality gate failed"
        exit 1
    fi
fi

cat results.txt
```

### Kubernetes Integration

```yaml
# testability-analysis.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: testability-analysis
spec:
  template:
    spec:
      containers:
      - name: testability-analyzer
        image: your-registry/testability-analyzer:latest
        command: ["analyze.sh", "src/", "json", "70"]
        volumeMounts:
        - name: source-code
          mountPath: /app/src
          readOnly: true
      volumes:
      - name: source-code
        configMap:
          name: source-code
      restartPolicy: Never
```

### Monitoring Integration

```python
# testability_monitor.py
import json
import requests
import sys
from datetime import datetime

def send_to_monitoring(results, webhook_url):
    """Send testability results to monitoring system."""
    
    avg_score = results['summary']['score_statistics']['average']
    total_files = results['summary']['total_files']
    red_flags = results['summary']['total_red_flags']
    
    payload = {
        'timestamp': datetime.now().isoformat(),
        'metrics': {
            'testability_score': avg_score,
            'files_analyzed': total_files,
            'red_flags': red_flags
        },
        'status': 'pass' if avg_score >= 70 else 'fail'
    }
    
    requests.post(webhook_url, json=payload)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python testability_monitor.py <results.json> <webhook_url>")
        sys.exit(1)
    
    results_file = sys.argv[1]
    webhook_url = sys.argv[2]
    
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    send_to_monitoring(results, webhook_url)
```

### Custom Scripts

```python
# batch_analysis.py
import os
import subprocess
import json
from pathlib import Path

def analyze_repository(repo_path, output_dir):
    """Analyze entire repository and generate reports."""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all Python directories
    python_dirs = []
    for root, dirs, files in os.walk(repo_path):
        if any(f.endswith('.py') for f in files):
            python_dirs.append(root)
    
    results = {}
    
    for directory in python_dirs:
        relative_dir = os.path.relpath(directory, repo_path)
        print(f"Analyzing {relative_dir}...")
        
        # Run analysis
        cmd = ['testability-analyzer', directory, '--output', 'json']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            results[relative_dir] = json.loads(result.stdout)
            
            # Save individual report
            report_file = os.path.join(output_dir, f"{relative_dir.replace('/', '_')}.json")
            with open(report_file, 'w') as f:
                f.write(result.stdout)
        else:
            print(f"Failed to analyze {relative_dir}: {result.stderr}")
    
    # Generate summary report
    summary = generate_summary(results)
    
    with open(os.path.join(output_dir, 'summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)
    
    return summary

def generate_summary(results):
    """Generate summary report from all results."""
    
    total_files = sum(r['summary']['total_files'] for r in results.values())
    total_functions = sum(r['summary']['total_functions'] for r in results.values())
    total_red_flags = sum(r['summary']['total_red_flags'] for r in results.values())
    
    scores = [r['summary']['score_statistics']['average'] for r in results.values()]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    return {
        'repository_summary': {
            'total_files': total_files,
            'total_functions': total_functions,
            'total_red_flags': total_red_flags,
            'average_score': avg_score,
            'directories_analyzed': len(results)
        },
        'directory_results': results
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python batch_analysis.py <repo_path> <output_dir>")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    summary = analyze_repository(repo_path, output_dir)
    print(f"Analysis complete. Average score: {summary['repository_summary']['average_score']:.2f}")
```

These examples provide comprehensive integration options for various CI/CD platforms and use cases. Choose the configuration that best fits your project's needs and infrastructure.
