import csv

from django.shortcuts import render
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.models import User

from .models import (
    Partner, Client, Project,
    Environment, Server, Resource,
    Issue, InfraActivity,
)


def global_search(request):
    query = request.GET.get("q", "").strip()
    results = []

    if query:
        def add_results(qs, model_label, admin_prefix):
            for obj in qs[:25]:  # limit per model
                results.append({
                    "model": model_label,
                    "label": str(obj),
                    "admin_url": f"/admin/core/{admin_prefix}/{obj.pk}/change/",
                })

        # Partner
        add_results(
            Partner.objects.filter(
                Q(name__icontains=query) |
                Q(code__icontains=query) |
                Q(contact_person__icontains=query) |
                Q(contact_email__icontains=query)
            ),
            "Partner",
            "partner",
        )

        # Client
        add_results(
            Client.objects.filter(
                Q(name__icontains=query) |
                Q(code__icontains=query) |
                Q(contact_person__icontains=query) |
                Q(contact_email__icontains=query)
            ),
            "Client",
            "client",
        )

        # Project
        add_results(
            Project.objects.filter(
                Q(name__icontains=query) |
                Q(code__icontains=query) |
                Q(description__icontains=query)
            ),
            "Project",
            "project",
        )

        # Environment
        add_results(
            Environment.objects.filter(
                Q(name__icontains=query) |
                Q(base_url__icontains=query) |
                Q(notes__icontains=query)
            ),
            "Environment",
            "environment",
        )

        # Server
        add_results(
            Server.objects.filter(
                Q(name__icontains=query) |
                Q(ip_address__icontains=query) |
                Q(region__icontains=query)
            ),
            "Server",
            "server",
        )

        # Resource
        add_results(
            Resource.objects.filter(
                Q(name__icontains=query) |
                Q(resource_type__icontains=query) |
                Q(provider__icontains=query) |
                Q(identifier__icontains=query) |
                Q(connection_info__icontains=query)
            ),
            "Resource",
            "resource",
        )

        # Issue
        add_results(
            Issue.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(activity_type__icontains=query)
            ),
            "Issue",
            "issue",
        )

        # InfraActivity
        add_results(
            InfraActivity.objects.filter(
                Q(note__icontains=query) |
                Q(status__icontains=query)
            ),
            "Infra Activity",
            "infraactivity",
        )

        # Users
        for u in User.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )[:25]:
            results.append({
                "model": "User",
                "label": f"{u.username} ({u.email})",
                "admin_url": f"/admin/auth/user/{u.pk}/change/",
            })

    context = {
        "query": query,
        "results": results,
    }
    return render(request, "admin/global_search.html", context)


def export_infra_data(request):
    """
    Export CSV with:
    Partner | Client | Project | Environment | Resource | Issue Title |
    Status | Updated Date | Handled By | Estimated Hour | Actual Hour
    """

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="infra_desk_export.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Partner",
        "Client",
        "Project",
        "Environment",
        "Resource",
        "Issue Title",
        "Status",
        "Updated Date",
        "Handled By",
        "Estimated Hour",
        "Actual Hour",
    ])

    # Base queryset
    issues = (
        Issue.objects
        .select_related(
            "project__client__partner",
            "environment",
        )
        # ⬇️ removed prefetch_related("infraactivity_set")
    )

    for issue in issues:
        partner = (
            issue.project.client.partner.name
            if getattr(issue, "project", None)
            and getattr(issue.project, "client", None)
            and getattr(issue.project.client, "partner", None)
            else ""
        )
        client = (
            issue.project.client.name
            if getattr(issue, "project", None)
            and getattr(issue.project, "client", None)
            else ""
        )
        project = issue.project.name if getattr(issue, "project", None) else ""
        environment = issue.environment.name if getattr(issue, "environment", None) else ""

        # 🔹 Resources from same environment (comma-separated)
        if issue.environment:
            resources_qs = Resource.objects.filter(environment=issue.environment)
            resources = ", ".join(r.name for r in resources_qs)
        else:
            resources = ""

        # 🔹 Activities – assumes FK is InfraActivity.issue
        # If your FK is named differently, change `issue=issue` accordingly.
        activities = list(InfraActivity.objects.filter(issue=issue)) or [None]

        for activity in activities:
            if activity:
                handled_by = (
                    activity.handled_by.get_full_name()
                    or activity.handled_by.username
                    if getattr(activity, "handled_by", None)
                    else ""
                )
                estimated = getattr(activity, "estimated_hours", "")
                actual = getattr(activity, "actual_hours", "")
            else:
                handled_by = ""
                estimated = ""
                actual = ""

            writer.writerow([
                partner,
                client,
                project,
                environment,
                resources,
                issue.title,
                issue.status,
                issue.updated_at.strftime("%Y-%m-%d %H:%M") if getattr(issue, "updated_at", None) else "",
                handled_by,
                estimated,
                actual,
            ])

    return response
