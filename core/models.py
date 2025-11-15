from datetime import date

from django.db import models
from django.contrib.auth.models import User


class Partner(models.Model):
    """
    Top-level companies you consult for: Kamsoft, Kilowott, etc.
    """
    name = models.CharField(max_length=200, unique=True)
    code = models.SlugField(
        unique=True,
        help_text="Short code, e.g. kamsoft, kilowott"
    )
    contact_person = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Client(models.Model):
    """
    End clients under each partner.
    Example: Partner=Kilowott, Client=Gutta Fra Havet.
    """
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        related_name="clients",
    )
    name = models.CharField(max_length=200)
    code = models.SlugField(
        help_text="Short code, e.g. gutta, norisma"
    )
    contact_person = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("partner", "code")
        ordering = ["partner", "name"]

    def __str__(self) -> str:
        return f"{self.partner.name} / {self.name}"


class Project(models.Model):
    """
    Infra project for each client.
    Example: Gutta Website, Norisma Infra, etc.
    """
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    name = models.CharField(max_length=200)
    code = models.SlugField(
        help_text="Short code, e.g. infra-portal, shop-live"
    )
    description = models.TextField(blank=True)
    repo_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("client", "code")
        ordering = ["client", "name"]

    def __str__(self) -> str:
        return f"{self.client} / {self.name}"


class Environment(models.Model):
    """
    Dev / Staging / UAT / Prod etc. per project.
    """
    ENV_CHOICES = [
        ("dev", "Development"),
        ("staging", "Staging"),
        ("uat", "UAT"),
        ("prod", "Production"),
        ("other", "Other"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="environments",
    )
    name = models.CharField(
        max_length=100,
        help_text="Display name, e.g. Dev India, Prod EU",
    )
    env_type = models.CharField(
        max_length=20,
        choices=ENV_CHOICES,
        default="dev",
    )
    base_url = models.URLField(
        blank=True,
        null=True,
        help_text="Main site URL for this environment, if any.",
    )
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "name")
        ordering = ["project", "env_type", "name"]

    def __str__(self) -> str:
        return f"{self.project} / {self.name} ({self.env_type})"


class Server(models.Model):
    """
    Servers (VMs, containers host, etc.) under each environment.
    """
    PROVIDER_CHOICES = [
        ("aws", "AWS"),
        ("azure", "Azure"),
        ("gcp", "GCP"),
        ("vps", "VPS / Other"),
        ("onprem", "On-Premise"),
        ("other", "Other"),
    ]

    environment = models.ForeignKey(
        Environment,
        on_delete=models.CASCADE,
        related_name="servers",
    )
    name = models.CharField(
        max_length=200,
        help_text="e.g. app-1, db-1, nginx-proxy",
    )
    ip_address = models.GenericIPAddressField()
    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        default="other",
    )
    region = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g. eu-west-1",
    )
    ssh_user = models.CharField(max_length=100, blank=True)
    ssh_port = models.IntegerField(default=22)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["environment", "name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.ip_address})"


class Resource(models.Model):
    """
    Other infra resources: DBs, buckets, queues, DNS records, etc.
    """
    RESOURCE_TYPES = [
        ("db", "Database"),
        ("bucket", "Object Storage / Bucket"),
        ("queue", "Queue / Messaging"),
        ("cache", "Cache / Redis"),
        ("dns", "DNS / Domain"),
        ("other", "Other"),
    ]

    environment = models.ForeignKey(
        Environment,
        on_delete=models.CASCADE,
        related_name="resources",
    )
    name = models.CharField(max_length=200)
    resource_type = models.CharField(
        max_length=20,
        choices=RESOURCE_TYPES,
        default="other",
    )
    provider = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g. RDS, Cloud SQL, S3, Cloudflare",
    )
    identifier = models.CharField(
        max_length=255,
        blank=True,
        help_text="DB name, bucket name, queue name, etc.",
    )
    connection_info = models.TextField(
        blank=True,
        help_text="Notes: host:port, endpoint URL, etc.",
    )
    is_critical = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["environment", "resource_type", "name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.resource_type})"


class UserProfile(models.Model):
    """
    Map Django users to a default partner/client and role.
    Helpful for multi-tenant scoping later.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    partner = models.ForeignKey(
        Partner,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    role = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g. Consultant, DevOps, Viewer",
    )

    def __str__(self) -> str:
        return f"{self.user.username} - {self.role or 'No role'}"


class Issue(models.Model):
    """
    Daily issues / tasks linked to infra (project/env/resource).
    Used for planning and tracking work.
    """
    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("blocked", "Blocked"),
        ("done", "Done / Completed"),
        ("cancelled", "Cancelled"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="issues",
    )
    environment = models.ForeignKey(
        Environment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issues",
        help_text="Optional: specific environment for this issue.",
    )
    resource = models.ForeignKey(
        Resource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issues",
        help_text="Optional: specific resource (DB, bucket, DNS, etc.).",
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open",
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="medium",
    )

    activity_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g. SSL renew, DNS change, backup, migration",
    )

    activity_date = models.DateField(
        help_text="Planned or actual working date for this issue.",
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text="Target completion date.",
    )

    estimate_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Estimated hours (e.g. 1.5, 2.0).",
    )
    actual_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Total utilized hours across all activities.",
    )

    project_manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_issues",
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_issues",
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_issues",
        help_text="Person actually working on this issue.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-activity_date", "-created_at"]

    def __str__(self) -> str:
        return f"{self.project} - {self.title}"

    @property
    def delay_days(self) -> int:
        """
        Delay in days based on due_date.
        - If no due_date: 0
        - If not done: today - due_date
        - If done/cancelled: activity_date - due_date
        """
        if not self.due_date:
            return 0

        if self.status in ("done", "cancelled"):
            delta = self.activity_date - self.due_date
        else:
            delta = date.today() - self.due_date

        return max(delta.days, 0)


class InfraActivity(models.Model):
    """
    Daily work log entries for an Issue.
    Example: 'Changed DNS record', 'Checked SSL', 'Restarted server'
    """
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="activities",
    )
    activity_date = models.DateField(
        help_text="Date when this activity was done.",
    )
    status = models.CharField(
        max_length=20,
        blank=True,
        help_text="Optional: status after this activity (e.g. checked, verified).",
    )
    note = models.TextField(
        blank=True,
        help_text="Short description of what you did.",
    )
    hours_spent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Hours spent for this activity.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-activity_date", "-created_at"]

    def __str__(self) -> str:
        return f"{self.activity_date} - {self.issue.title}"
