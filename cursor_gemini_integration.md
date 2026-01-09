# 🚀 Gemini CLI Integration with Cursor for Google Cloud Management

## Overview

This guide explains how to integrate the Gemini CLI with Cursor to enhance your Google Cloud management capabilities. The Gemini CLI provides AI-powered assistance for cloud architecture analysis, cost optimization, security auditing, and more.

## 🎯 Benefits of Gemini + Cursor Integration

### **Enhanced Development Experience**
- **AI-Powered Code Review**: Get intelligent suggestions for your Google Cloud code
- **Architecture Analysis**: Analyze your cloud infrastructure with Gemini's expertise
- **Cost Optimization**: Get detailed cost-saving recommendations
- **Security Auditing**: Generate comprehensive security policies
- **Documentation Generation**: Auto-generate documentation for your infrastructure

### **Google Cloud Expertise**
- **Native Google Product**: Gemini has deep knowledge of Google Cloud services
- **Best Practices**: Leverage Google's own AI for cloud best practices
- **Real-time Analysis**: Get instant feedback on your cloud configurations
- **Terraform Generation**: Generate infrastructure as code automatically

## 🛠️ Setup Instructions

### 1. Install Dependencies

```bash
# Install the required packages
pip install -r ../shared/dependencies/google_cloud_agent.txt

# Make the CLI executable
chmod +x gemini_cli.py
```

### 2. Configure Environment

```bash
# Copy the environment template
cp env.example .env

# Edit the .env file with your credentials
nano .env
```

**Required Environment Variables:**
```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# OpenAI (for existing features)
OPENAI_API_KEY=your-openai-key

# Google Gemini (NEW)
GOOGLE_API_KEY=your-gemini-api-key
```

### 3. Get Gemini API Key

1. **Visit Google AI Studio**: https://makersuite.google.com/app/apikey
2. **Create API Key**: Generate a new API key for Gemini
3. **Add to .env**: Set `GOOGLE_API_KEY=your-key-here`

### 4. Configure Google Cloud

```bash
# Authenticate with Google Cloud
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

## 🎮 Using Gemini CLI in Cursor

### **Basic Commands**

#### **Architecture Analysis**
```bash
# Analyze your cloud architecture
python gemini_cli.py analyze-architecture your-project-id

# Save results to file
python gemini_cli.py analyze-architecture your-project-id --output analysis.json
```

#### **Cost Optimization**
```bash
# Get cost optimization recommendations
python gemini_cli.py optimize-costs your-project-id

# Save detailed analysis
python gemini_cli.py optimize-costs your-project-id --output cost-analysis.json
```

#### **Terraform Generation**
```bash
# Generate Terraform configuration
python gemini_cli.py generate-terraform "web application with load balancer and database"

# Specify output directory
python gemini_cli.py generate-terraform "microservices architecture" --output-dir ./infrastructure
```

#### **Code Review**
```bash
# Review a specific file
python gemini_cli.py review-code app/main.py

# Review with context
python gemini_cli.py review-code app/services/gcp_service.py --context "Google Cloud service integration"
```

#### **Documentation Generation**
```bash
# Generate README for a file
python gemini_cli.py generate-docs app/main.py --type README

# Generate API documentation
python gemini_cli.py generate-docs app/main.py --type API --output docs/api.md
```

#### **Security Audit**
```bash
# Generate security policies
python gemini_cli.py security-audit your-project-id

# With specific requirements
python gemini_cli.py security-audit your-project-id --requirements "HIPAA compliance, encryption at rest"
```

#### **Resource Listing**
```bash
# List all resources
python gemini_cli.py list-resources

# List resources for specific project
python gemini_cli.py list-resources --project your-project-id
```

#### **Get Recommendations**
```bash
# Get intelligent recommendations
python gemini_cli.py get-recommendations

# For specific project
python gemini_cli.py get-recommendations --project your-project-id
```

## 🔧 Cursor Integration Tips

### **1. Terminal Integration**

Open Cursor's integrated terminal and run Gemini CLI commands:

```bash
# In Cursor terminal
python gemini_cli.py analyze-architecture my-project
```

### **2. Task Automation**

Create Cursor tasks for common operations:

```json
// .vscode/tasks.json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Analyze Architecture",
            "type": "shell",
            "command": "python",
            "args": ["gemini_cli.py", "analyze-architecture", "${input:projectId}"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        },
        {
            "label": "Cost Optimization",
            "type": "shell",
            "command": "python",
            "args": ["gemini_cli.py", "optimize-costs", "${input:projectId}"],
            "group": "build"
        },
        {
            "label": "Code Review",
            "type": "shell",
            "command": "python",
            "args": ["gemini_cli.py", "review-code", "${file}"],
            "group": "build"
        }
    ],
    "inputs": [
        {
            "id": "projectId",
            "type": "promptString",
            "description": "Google Cloud Project ID"
        }
    ]
}
```

### **3. Keyboard Shortcuts**

Add keyboard shortcuts for quick access:

```json
// .vscode/keybindings.json
[
    {
        "key": "ctrl+shift+g a",
        "command": "workbench.action.tasks.runTask",
        "args": "Analyze Architecture"
    },
    {
        "key": "ctrl+shift+g c",
        "command": "workbench.action.tasks.runTask",
        "args": "Cost Optimization"
    },
    {
        "key": "ctrl+shift+g r",
        "command": "workbench.action.tasks.runTask",
        "args": "Code Review"
    }
]
```

### **4. Snippets**

Create code snippets for common Gemini CLI patterns:

```json
// .vscode/snippets.json
{
    "Gemini Architecture Analysis": {
        "prefix": "gemini-arch",
        "body": [
            "python gemini_cli.py analyze-architecture ${1:project-id} --output ${2:analysis.json}"
        ],
        "description": "Analyze cloud architecture with Gemini"
    },
    "Gemini Cost Optimization": {
        "prefix": "gemini-cost",
        "body": [
            "python gemini_cli.py optimize-costs ${1:project-id} --output ${2:cost-analysis.json}"
        ],
        "description": "Get cost optimization recommendations"
    },
    "Gemini Terraform Generation": {
        "prefix": "gemini-terraform",
        "body": [
            "python gemini_cli.py generate-terraform \"${1:requirements}\" --output-dir ${2:./terraform}"
        ],
        "description": "Generate Terraform configuration"
    }
}
```

## 📊 Example Workflows

### **1. New Project Setup**

```bash
# 1. Analyze current architecture
python gemini_cli.py analyze-architecture my-new-project

# 2. Generate Terraform configuration
python gemini_cli.py generate-terraform "web application with auto-scaling, load balancer, and managed database"

# 3. Review generated code
python gemini_cli.py review-code terraform/main.tf

# 4. Generate documentation
python gemini_cli.py generate-docs terraform/main.tf --type README --output terraform/README.md
```

### **2. Cost Optimization Session**

```bash
# 1. Get current cost analysis
python gemini_cli.py optimize-costs my-project --output current-costs.json

# 2. List resources to understand usage
python gemini_cli.py list-resources --project my-project

# 3. Get recommendations
python gemini_cli.py get-recommendations --project my-project

# 4. Review specific recommendations
python gemini_cli.py analyze-architecture my-project --output detailed-analysis.json
```

### **3. Security Audit**

```bash
# 1. Generate security policies
python gemini_cli.py security-audit my-project --requirements "SOC2 compliance, encryption at rest and in transit"

# 2. Review current IAM policies
python gemini_cli.py list-resources --project my-project

# 3. Generate compliance documentation
python gemini_cli.py generate-docs security-policies.json --type COMPLIANCE --output compliance-report.md
```

## 🎨 Advanced Features

### **1. Custom Analysis Scripts**

Create custom scripts that combine multiple Gemini CLI commands:

```python
#!/usr/bin/env python3
# custom_analysis.py

import asyncio
import subprocess
import json
from pathlib import Path

async def comprehensive_analysis(project_id: str):
    """Run comprehensive analysis using Gemini CLI"""
    
    # Architecture analysis
    result1 = subprocess.run([
        "python", "gemini_cli.py", "analyze-architecture", 
        project_id, "--output", "architecture.json"
    ], capture_output=True, text=True)
    
    # Cost optimization
    result2 = subprocess.run([
        "python", "gemini_cli.py", "optimize-costs", 
        project_id, "--output", "costs.json"
    ], capture_output=True, text=True)
    
    # Security audit
    result3 = subprocess.run([
        "python", "gemini_cli.py", "security-audit", 
        project_id, "--output", "security.json"
    ], capture_output=True, text=True)
    
    # Combine results
    combined_report = {
        "project_id": project_id,
        "architecture": json.loads(Path("architecture.json").read_text()) if Path("architecture.json").exists() else {},
        "costs": json.loads(Path("costs.json").read_text()) if Path("costs.json").exists() else {},
        "security": json.loads(Path("security.json").read_text()) if Path("security.json").exists() else {}
    }
    
    # Save combined report
    with open("comprehensive-analysis.json", "w") as f:
        json.dump(combined_report, f, indent=2)
    
    print("✅ Comprehensive analysis complete!")

if __name__ == "__main__":
    import sys
    project_id = sys.argv[1] if len(sys.argv) > 1 else "default-project"
    asyncio.run(comprehensive_analysis(project_id))
```

### **2. Integration with Existing Workflows**

Add Gemini CLI to your existing CI/CD pipelines:

```yaml
# .github/workflows/gemini-analysis.yml
name: Gemini Cloud Analysis

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r ../shared/dependencies/google_cloud_agent.txt
    
    - name: Configure Google Cloud
      run: |
        echo ${{ secrets.GCP_SA_KEY }} > service-account.json
        export GOOGLE_APPLICATION_CREDENTIALS=service-account.json
    
    - name: Run Gemini Analysis
      run: |
        python gemini_cli.py analyze-architecture ${{ secrets.GCP_PROJECT_ID }} --output analysis.json
        python gemini_cli.py optimize-costs ${{ secrets.GCP_PROJECT_ID }} --output costs.json
    
    - name: Upload Analysis Results
      uses: actions/upload-artifact@v2
      with:
        name: gemini-analysis
        path: |
          analysis.json
          costs.json
```

## 🔍 Troubleshooting

### **Common Issues**

#### **1. Gemini API Key Not Found**
```bash
Error: Google API key not found. Gemini features will be limited.
```
**Solution**: Set `GOOGLE_API_KEY` in your `.env` file

#### **2. Google Cloud Authentication**
```bash
Error: Google Cloud credentials not found
```
**Solution**: Run `gcloud auth application-default login`

#### **3. Project ID Issues**
```bash
Error: Project ID not configured
```
**Solution**: Set `GOOGLE_CLOUD_PROJECT_ID` in your `.env` file

#### **4. Permission Errors**
```bash
Error: Permission denied for project
```
**Solution**: Ensure your service account has the necessary IAM roles

### **Debug Mode**

Enable debug mode for detailed logging:

```bash
# Set in .env file
DEBUG=true

# Or run with debug flag
python gemini_cli.py analyze-architecture my-project --debug
```

## 📈 Best Practices

### **1. Regular Analysis**
- Run architecture analysis weekly
- Monitor costs monthly
- Perform security audits quarterly

### **2. Documentation**
- Generate documentation for all infrastructure changes
- Keep analysis reports for historical comparison
- Document security policies and compliance requirements

### **3. Integration**
- Integrate Gemini CLI into your development workflow
- Use it for code reviews before merging
- Include it in your CI/CD pipeline

### **4. Security**
- Never commit API keys to version control
- Use environment variables for sensitive data
- Regularly rotate API keys

## 🚀 Future Enhancements

### **Planned Features**
- **Real-time Monitoring**: Continuous analysis of cloud resources
- **Automated Remediation**: Auto-fix common issues
- **Multi-cloud Support**: Extend to AWS and Azure
- **Advanced Analytics**: Machine learning insights
- **Team Collaboration**: Share analysis results with team members

### **Custom Extensions**
- **Custom Models**: Train Gemini on your specific use cases
- **Integration APIs**: Connect with other tools and services
- **Plugin System**: Extend functionality with custom plugins

---

## 📞 Support

For additional support:

- **Documentation**: Check the `/docs` folder
- **Issues**: Report bugs and feature requests
- **Community**: Join discussions and share experiences
- **Google AI Studio**: https://makersuite.google.com/

---

*This integration guide helps you leverage the power of Gemini AI within Cursor for enhanced Google Cloud management. The combination provides a powerful development environment for cloud infrastructure management.* 