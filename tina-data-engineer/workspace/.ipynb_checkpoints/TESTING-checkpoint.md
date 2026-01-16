# Testing Guide

## Test Files Created

### 1. validation.ipynb
**Purpose**: Test all environment components from Jupyter Notebook
**How to use**:
1. Open http://localhost:8888
2. Click on `validation.ipynb`
3. Run all cells (Cell > Run All)
4. Check for ✅ marks

### 2. sample_data.csv
**Purpose**: Sample data for testing
**Contents**: 10 employee records with name, age, city, salary

### 3. test_processing.py
**Purpose**: Test pandas and data processing from terminal
**How to run**:
```bash
# From your Mac terminal
docker exec -it tina-devtools bash
cd /workspace
python test_processing.py
```

Or from VS Code terminal after connecting to the container.

### 4. test_terraform.tf
**Purpose**: Test Terraform and AWS integration
**How to use**:
```bash
# From container terminal
docker exec -it tina-devtools bash
cd /workspace

# Initialize Terraform
terraform init

# Plan (preview changes)
terraform plan

# Apply (create resources) - ONLY IF YOU WANT TO CREATE REAL AWS RESOURCES
terraform apply

# Destroy (clean up) - IMPORTANT: Run this after testing
terraform destroy
```

**⚠️ WARNING**: Running `terraform apply` will create real AWS resources that may incur charges. Only run if you have AWS credentials configured and understand the costs.

## Quick Test Checklist

- [ ] Open Jupyter at http://localhost:8888
- [ ] Run validation.ipynb - all tests pass
- [ ] Run test_processing.py from terminal
- [ ] Check processed_data.csv is created
- [ ] (Optional) Test Terraform if AWS credentials are configured

## Expected Results

### validation.ipynb
- MySQL connection: ✅
- PostgreSQL connection: ✅
- AWS CLI: ✅
- Terraform: ✅
- Git: ✅
- Python packages: ✅

### test_processing.py
- Loads CSV
- Calculates statistics
- Groups data by city
- Filters high earners
- Creates new column
- Exports processed_data.csv

### Terraform (if tested)
- Creates security group in AWS
- Shows security group ID
- Can be destroyed cleanly
