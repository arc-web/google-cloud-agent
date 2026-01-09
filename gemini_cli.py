#!/usr/bin/env python3
"""
Gemini CLI for Google Cloud Management
A command-line interface that integrates with Cursor for enhanced Google Cloud management
"""

import click
import typer
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

from app.services.gemini_service import GeminiService
from app.services.google_cloud_service import GoogleCloudService
from app.services.recommendation_service import RecommendationService

console = Console()
app = typer.Typer(help="Gemini CLI for Google Cloud Management")

# Initialize services
gemini_service = GeminiService()
gcp_service = GoogleCloudService()
recommendation_service = RecommendationService()

@app.command()
def analyze_architecture(
    project_id: str = typer.Argument(..., help="Google Cloud Project ID"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file for results")
):
    """Analyze Google Cloud architecture using Gemini"""
    console.print(f"[bold blue]🔍 Analyzing architecture for project: {project_id}[/bold blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing architecture...", total=None)
        
        try:
            # Run the analysis
            result = asyncio.run(gemini_service.analyze_cloud_architecture(project_id))
            
            if "error" in result:
                console.print(f"[bold red]❌ Error: {result['error']}[/bold red]")
                return
            
            # Display results
            display_architecture_analysis(result, output_file)
            
        except Exception as e:
            console.print(f"[bold red]❌ Error during analysis: {e}[/bold red]")

@app.command()
def optimize_costs(
    project_id: str = typer.Argument(..., help="Google Cloud Project ID"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file for results")
):
    """Get cost optimization recommendations using Gemini"""
    console.print(f"[bold blue]💰 Analyzing costs for project: {project_id}[/bold blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing costs...", total=None)
        
        try:
            # Get current costs
            costs = asyncio.run(gcp_service.estimate_costs())
            
            # Get optimization recommendations
            result = asyncio.run(gemini_service.optimize_cloud_costs(costs))
            
            if "error" in result:
                console.print(f"[bold red]❌ Error: {result['error']}[/bold red]")
                return
            
            # Display results
            display_cost_optimization(result, output_file)
            
        except Exception as e:
            console.print(f"[bold red]❌ Error during cost analysis: {e}[/bold red]")

@app.command()
def generate_terraform(
    requirements: str = typer.Argument(..., help="Requirements description"),
    output_dir: str = typer.Option("./terraform", "--output-dir", "-o", help="Output directory for Terraform files")
):
    """Generate Terraform configuration using Gemini"""
    console.print(f"[bold blue]🏗️ Generating Terraform configuration[/bold blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Generating Terraform config...", total=None)
        
        try:
            # Generate Terraform configuration
            result = asyncio.run(gemini_service.generate_terraform_config(requirements))
            
            if "error" in result:
                console.print(f"[bold red]❌ Error: {result['error']}[/bold red]")
                return
            
            # Save files
            save_terraform_files(result, output_dir)
            
        except Exception as e:
            console.print(f"[bold red]❌ Error generating Terraform: {e}[/bold red]")

@app.command()
def review_code(
    file_path: str = typer.Argument(..., help="Path to the code file to review"),
    context: Optional[str] = typer.Option("", "--context", "-c", help="Additional context for the review")
):
    """Review code using Gemini"""
    console.print(f"[bold blue]🔍 Reviewing code: {file_path}[/bold blue]")
    
    try:
        # Read the code file
        with open(file_path, 'r') as f:
            code = f.read()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Reviewing code...", total=None)
            
            # Get code review
            result = asyncio.run(gemini_service.code_review_and_suggestions(code, context))
            
            if "error" in result:
                console.print(f"[bold red]❌ Error: {result['error']}[/bold red]")
                return
            
            # Display results
            display_code_review(result)
            
    except FileNotFoundError:
        console.print(f"[bold red]❌ File not found: {file_path}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]❌ Error reviewing code: {e}[/bold red]")

@app.command()
def generate_docs(
    file_path: str = typer.Argument(..., help="Path to the file to document"),
    doc_type: str = typer.Option("README", "--type", "-t", help="Type of documentation to generate"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file for documentation")
):
    """Generate documentation using Gemini"""
    console.print(f"[bold blue]📚 Generating {doc_type} documentation[/bold blue]")
    
    try:
        # Read the file
        with open(file_path, 'r') as f:
            content = f.read()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating documentation...", total=None)
            
            # Generate documentation
            result = asyncio.run(gemini_service.generate_documentation(content, doc_type))
            
            if "error" in result:
                console.print(f"[bold red]❌ Error: {result['error']}[/bold red]")
                return
            
            # Display and save results
            display_documentation(result, output_file)
            
    except FileNotFoundError:
        console.print(f"[bold red]❌ File not found: {file_path}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]❌ Error generating documentation: {e}[/bold red]")

@app.command()
def security_audit(
    project_id: str = typer.Argument(..., help="Google Cloud Project ID"),
    requirements: Optional[str] = typer.Option("", "--requirements", "-r", help="Security requirements"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file for results")
):
    """Generate security policies using Gemini"""
    console.print(f"[bold blue]🔒 Generating security policies for project: {project_id}[/bold blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Generating security policies...", total=None)
        
        try:
            # Generate security policies
            result = asyncio.run(gemini_service.generate_security_policy(requirements))
            
            if "error" in result:
                console.print(f"[bold red]❌ Error: {result['error']}[/bold red]")
                return
            
            # Display results
            display_security_policies(result, output_file)
            
        except Exception as e:
            console.print(f"[bold red]❌ Error generating security policies: {e}[/bold red]")

@app.command()
def list_resources(
    project_id: Optional[str] = typer.Option(None, "--project", "-p", help="Google Cloud Project ID")
):
    """List Google Cloud resources"""
    console.print(f"[bold blue]📋 Listing Google Cloud resources[/bold blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Fetching resources...", total=None)
        
        try:
            # Get resources
            instances = asyncio.run(gcp_service.list_instances(project_id))
            buckets = asyncio.run(gcp_service.list_storage_buckets())
            datasets = asyncio.run(gcp_service.list_bigquery_datasets())
            
            # Display results
            display_resources(instances, buckets, datasets)
            
        except Exception as e:
            console.print(f"[bold red]❌ Error listing resources: {e}[/bold red]")

@app.command()
def get_recommendations(
    project_id: Optional[str] = typer.Option(None, "--project", "-p", help="Google Cloud Project ID")
):
    """Get intelligent recommendations"""
    console.print(f"[bold blue]💡 Getting intelligent recommendations[/bold blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Generating recommendations...", total=None)
        
        try:
            # Get recommendations
            recommendations = asyncio.run(recommendation_service.get_recommendations("cli_user"))
            
            # Display results
            display_recommendations(recommendations)
            
        except Exception as e:
            console.print(f"[bold red]❌ Error getting recommendations: {e}[/bold red]")

def display_architecture_analysis(result: dict, output_file: Optional[str]):
    """Display architecture analysis results"""
    console.print("\n[bold green]✅ Architecture Analysis Complete[/bold green]\n")
    
    # Create a table for the overview
    table = Table(title="Architecture Overview")
    table.add_column("Component", style="cyan")
    table.add_column("Details", style="white")
    
    if "architecture_overview" in result:
        table.add_row("Overview", result["architecture_overview"])
    
    if "security_assessment" in result:
        security = result["security_assessment"]
        table.add_row("Security Score", f"{security.get('score', 'N/A')}/100")
        table.add_row("Security Issues", str(len(security.get("issues", []))))
    
    if "cost_optimization" in result:
        cost_opt = result["cost_optimization"]
        table.add_row("Estimated Savings", cost_opt.get("estimated_savings", "N/A"))
    
    console.print(table)
    
    # Display detailed sections
    if "security_assessment" in result:
        display_security_section(result["security_assessment"])
    
    if "cost_optimization" in result:
        display_cost_section(result["cost_optimization"])
    
    if "performance_recommendations" in result:
        display_performance_section(result["performance_recommendations"])
    
    # Save to file if requested
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        console.print(f"\n[bold green]💾 Results saved to: {output_file}[/bold green]")

def display_cost_optimization(result: dict, output_file: Optional[str]):
    """Display cost optimization results"""
    console.print("\n[bold green]✅ Cost Analysis Complete[/bold green]\n")
    
    # Display cost analysis
    if "cost_analysis" in result:
        console.print(Panel(result["cost_analysis"], title="Cost Analysis", border_style="blue"))
    
    # Display recommendations
    if "recommendations" in result:
        table = Table(title="Cost Optimization Recommendations")
        table.add_column("Recommendation", style="cyan")
        table.add_column("Savings", style="green")
        table.add_column("Effort", style="yellow")
        table.add_column("Risk", style="red")
        
        for rec in result["recommendations"]:
            table.add_row(
                rec.get("title", "N/A"),
                rec.get("estimated_savings", "N/A"),
                rec.get("effort", "N/A"),
                rec.get("risk_level", "N/A")
            )
        
        console.print(table)
    
    # Display total savings
    if "total_potential_savings" in result:
        console.print(f"\n[bold green]💰 Total Potential Savings: {result['total_potential_savings']}[/bold green]")
    
    # Save to file if requested
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        console.print(f"\n[bold green]💾 Results saved to: {output_file}[/bold green]")

def save_terraform_files(result: dict, output_dir: str):
    """Save Terraform files to the specified directory"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    files_created = []
    
    for filename, content in result.items():
        if filename.endswith('.tf') or filename.endswith('.md') or filename.endswith('.example'):
            file_path = output_path / filename
            with open(file_path, 'w') as f:
                f.write(content)
            files_created.append(filename)
    
    console.print(f"\n[bold green]✅ Terraform files created in: {output_dir}[/bold green]")
    console.print(f"Files created: {', '.join(files_created)}")

def display_code_review(result: dict):
    """Display code review results"""
    console.print("\n[bold green]✅ Code Review Complete[/bold green]\n")
    
    # Display quality assessment
    if "quality_assessment" in result:
        quality = result["quality_assessment"]
        console.print(f"[bold]Quality Score: {quality.get('score', 'N/A')}/100[/bold]")
        
        if quality.get("issues"):
            console.print("\n[bold red]Issues Found:[/bold red]")
            for issue in quality["issues"]:
                console.print(f"  • {issue}")
        
        if quality.get("strengths"):
            console.print("\n[bold green]Strengths:[/bold green]")
            for strength in quality["strengths"]:
                console.print(f"  • {strength}")
    
    # Display security review
    if "security_review" in result:
        security = result["security_review"]
        if security.get("vulnerabilities"):
            console.print("\n[bold red]Security Vulnerabilities:[/bold red]")
            for vuln in security["vulnerabilities"]:
                console.print(f"  • {vuln}")
    
    # Display improvements
    if "improvements" in result:
        console.print("\n[bold blue]Suggested Improvements:[/bold blue]")
        for improvement in result["improvements"]:
            console.print(f"\n[bold]{improvement.get('type', 'Improvement')}:[/bold]")
            console.print(f"  {improvement.get('description', '')}")
            if improvement.get('code_example'):
                console.print(f"  [dim]Example:[/dim] {improvement['code_example']}")

def display_documentation(result: dict, output_file: Optional[str]):
    """Display documentation results"""
    console.print("\n[bold green]✅ Documentation Generated[/bold green]\n")
    
    # Display full documentation
    if "full_documentation" in result:
        md = Markdown(result["full_documentation"])
        console.print(md)
    
    # Save to file if requested
    if output_file:
        with open(output_file, 'w') as f:
            if "full_documentation" in result:
                f.write(result["full_documentation"])
            else:
                json.dump(result, f, indent=2)
        console.print(f"\n[bold green]💾 Documentation saved to: {output_file}[/bold green]")

def display_security_policies(result: dict, output_file: Optional[str]):
    """Display security policies results"""
    console.print("\n[bold green]✅ Security Policies Generated[/bold green]\n")
    
    # Display IAM policies
    if "iam_policies" in result:
        iam = result["iam_policies"]
        console.print("[bold blue]IAM Policies:[/bold blue]")
        if iam.get("roles"):
            console.print("  Roles:")
            for role in iam["roles"]:
                console.print(f"    • {role}")
    
    # Display network security
    if "network_security" in result:
        network = result["network_security"]
        console.print("\n[bold blue]Network Security:[/bold blue]")
        if network.get("firewall_rules"):
            console.print("  Firewall Rules:")
            for rule in network["firewall_rules"]:
                console.print(f"    • {rule}")
    
    # Save to file if requested
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        console.print(f"\n[bold green]💾 Security policies saved to: {output_file}[/bold green]")

def display_resources(instances: list, buckets: list, datasets: list):
    """Display Google Cloud resources"""
    console.print("\n[bold green]✅ Resources Retrieved[/bold green]\n")
    
    # Display instances
    if instances:
        table = Table(title="Compute Instances")
        table.add_column("Name", style="cyan")
        table.add_column("Zone", style="blue")
        table.add_column("Status", style="green")
        table.add_column("Machine Type", style="yellow")
        
        for instance in instances:
            table.add_row(
                instance.get("name", "N/A"),
                instance.get("zone", "N/A"),
                instance.get("status", "N/A"),
                instance.get("machine_type", "N/A")
            )
        console.print(table)
    else:
        console.print("[yellow]No compute instances found[/yellow]")
    
    # Display buckets
    if buckets:
        table = Table(title="Storage Buckets")
        table.add_column("Name", style="cyan")
        table.add_column("Location", style="blue")
        table.add_column("Storage Class", style="green")
        
        for bucket in buckets:
            table.add_row(
                bucket.get("name", "N/A"),
                bucket.get("location", "N/A"),
                bucket.get("storage_class", "N/A")
            )
        console.print(table)
    else:
        console.print("[yellow]No storage buckets found[/yellow]")

def display_recommendations(recommendations: list):
    """Display recommendations"""
    console.print("\n[bold green]✅ Recommendations Generated[/bold green]\n")
    
    if recommendations:
        table = Table(title="Intelligent Recommendations")
        table.add_column("Title", style="cyan")
        table.add_column("Category", style="blue")
        table.add_column("Priority", style="yellow")
        table.add_column("Savings", style="green")
        
        for rec in recommendations:
            table.add_row(
                rec.title,
                rec.category,
                rec.priority,
                f"${rec.estimated_savings}" if rec.estimated_savings else "N/A"
            )
        console.print(table)
    else:
        console.print("[yellow]No recommendations available[/yellow]")

def display_security_section(security: dict):
    """Display security assessment section"""
    console.print("\n[bold blue]🔒 Security Assessment[/bold blue]")
    
    if security.get("issues"):
        console.print("\n[bold red]Security Issues:[/bold red]")
        for issue in security["issues"]:
            console.print(f"  • {issue}")
    
    if security.get("recommendations"):
        console.print("\n[bold green]Security Recommendations:[/bold green]")
        for rec in security["recommendations"]:
            console.print(f"  • {rec}")

def display_cost_section(cost_opt: dict):
    """Display cost optimization section"""
    console.print("\n[bold blue]💰 Cost Optimization[/bold blue]")
    
    if cost_opt.get("opportunities"):
        console.print("\n[bold green]Optimization Opportunities:[/bold green]")
        for opp in cost_opt["opportunities"]:
            console.print(f"  • {opp}")

def display_performance_section(recommendations: list):
    """Display performance recommendations section"""
    console.print("\n[bold blue]⚡ Performance Recommendations[/bold blue]")
    
    for rec in recommendations:
        console.print(f"  • {rec}")

if __name__ == "__main__":
    app() 