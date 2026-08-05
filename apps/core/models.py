from django.db import models


DEFAULT_PRIVACY_POLICY = """# Privacy Policy

**Effective Date:** July 20, 2026  
**Last Updated:** July 20, 2026  

Welcome to **Viskotu** ("we," "our," or "us"). We respect your privacy and are committed to protecting the personal data of our users, including Advertisers, Space Owners, and Production Partners (Printers). This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you visit our web platform and utilize our advertising space management and print workflow services.

---

## 1. Information We Collect

We collect information that you provide directly to us when setting up an account, listing space inventory, ad_placement ad placements, or communicating with customer support:

* **Account & Contact Information:** Name, email address, phone number, company name, and profile avatar.
* **Verification & KYC Data:** Government-issued identification, business registration documents, and tax identification numbers required to verify Space Owners and Printers before payouts.
* **Financial & Transactional Data:** Billing addresses, bank details, and payment transaction logs processed securely through our verified payment partners.
* **Operational Data:** Ad campaign specifications, creative artwork files, print job acceptance metrics, and physical verification proofs (such as photos of installed advertisements).

---

## 2. How We Use Your Information

We use the collected information for the following core purposes:

1. **Platform Operation:** To facilitate ad_placements, coordinate print job assignments, and maintain real-time campaign status tracking across Advertisers, Space Owners, and Printers.
2. **Account Security & KYC:** To verify identity, prevent fraud, enforce our Service Level Agreements (SLAs), and maintain system integrity.
3. **Financial Processing:** To process escrow payments, calculate commission splits, and disburse payouts upon verified ad placement completion (`POP_VERIFIED`).
4. **Platform Communications:** To send automated notifications regarding ad_placement status changes, print job deadlines, dispute alerts, and system operational updates.
5. **Continuous Improvement:** To analyze usage trends, optimize platform reliability algorithms, and enhance user experience.

---

## 3. Sharing & Disclosure of Information

We do not sell your personal data. We disclose information only under the following circumstances:

* **Between Transactional Parties:** When a campaign is booked, necessary contact information and creative specifications are shared between the Advertiser, the selected Space Owner, and the assigned Printer to ensure seamless physical ad installation.
* **Service Providers:** With trusted third-party vendors who provide cloud hosting, payment processing, identity verification, and email delivery services under strict data confidentiality terms.
* **Legal Compliance:** When required by applicable laws, court orders, or lawful government inquiries, or to defend our legal rights and enforce platform terms.

---

## 4. Data Retention & Security

We implement robust technical and organizational security measures to protect your data against unauthorized access, loss, or alteration. We retain personal and transactional records for as long as your account remains active or as required by financial regulations and tax compliance obligations.

---

## 5. Your Privacy Rights & Choices

Depending on your jurisdiction, you may have the right to:

* Access, review, and request a copy of the personal data we hold about you.
* Request correction of inaccurate or incomplete profile information.
* Request account deletion and anonymization of personal data, subject to active ad_placement obligations and mandatory regulatory retention periods.
* Opt out of non-essential promotional communications at any time.

---

## 6. Contact Us

If you have questions, concerns, or requests regarding this Privacy Policy or our data processing practices, please contact our Data Protection Team:

* **Email:** privacy@viskotu.com
* **Address:** Viskotu Legal & Compliance Department, 100 Innovation Way, Suite 400
"""

DEFAULT_TERMS_OF_SERVICE = """# Terms of Service

**Effective Date:** July 20, 2026  
**Last Updated:** July 20, 2026  

Welcome to **Viskotu**. By accessing our website, creating an account, or using our platform to list advertising inventory, launch campaigns, or accept print production jobs, you agree to be bound by these Terms of Service ("Terms"). If you do not agree to these Terms, you may not access or use the platform.

---

## 1. Platform Overview & User Roles

Viskotu is a multi-sided marketplace and production coordination platform that connects three primary user roles:

1. **Advertisers:** Entities seeking to discover, book, and monitor physical ad placements across verified space listings.
2. **Space Owners:** Individuals or businesses listing commercial property, billboards, storefronts, or indoor spaces available for physical ad installation.
3. **Printers (Production Partners):** Verified print and installation specialists responsible for manufacturing physical banners and executing on-site ad installation according to campaign specifications.

---

## 2. Account Registration & Eligibility

To use Viskotu, you must register for an account and provide accurate, complete information. 
* You must be at least 18 years old and possess legal capacity to enter into binding agreements.
* **Space Owners and Printers** must undergo mandatory Know Your Customer (KYC) identity and business verification prior to publishing listings or receiving payout disbursements.
* You are responsible for maintaining the confidentiality of your login credentials and for all activities that occur under your account.

---

## 3. AdPlacement Workflow & Escrow Payments

All ad_placements executed on Viskotu follow a rigorous, stage-gated lifecycle:

1. **Campaign Creation & Escrow:** When an Advertiser initiates a ad_placement, the total campaign cost (including space rental, printing, and platform service fees) is deposited into secure platform escrow.
2. **Job Acceptance:** The assigned Printer must accept the print job within the designated SLA window (`SLA_PRINT_ACCEPTANCE`).
3. **Production & Installation:** The Printer produces the physical assets and installs them at the Space Owner's designated location.
4. **Proof of Performance (POP):** The Printer or Space Owner uploads photographic and geotagged proof (`POP_AWAITING`). Once verified (`POP_VERIFIED`), escrow funds are released according to the agreed commission schedule.

---

## 4. Service Level Agreements (SLAs) & Forfeitures

To ensure platform reliability and maintain trust across parties, users agree to abide by strict SLAs:

* Failure by a Printer to accept or complete a print job within the agreed SLA deadlines may trigger automatic job reallocation (`JOB_FORFEITED`) and potential penalty deductions from future earnings.
* Space Owners must maintain the physical ad installation in good condition throughout the contracted display duration. Unauthorized early removal constitutes a material breach and triggers pro-rata refunds to the Advertiser.

---

## 5. Cancellation & Refund Terms

Cancellations are governed by the platform's standardized cancellation policy (`CancellationTerms`):

* **Before Print Job Acceptance:** Advertisers may cancel ad_placements with a full refund of escrowed funds, less standard payment processing fees.
* **After Print Production Has Begun:** If a campaign is canceled after the Printer has initiated material production, printing costs are non-refundable and will be disbursed to the Printer to cover expenses.
* **Owner/Printer Default:** If a Space Owner or Printer defaults or fails to fulfill their obligations, the Advertiser receives a 100% full refund or immediate replacement placement at no extra cost.

---

## 6. Prohibited Conduct

Users strictly agree **not** to:

* Submit false or misleading listing details, counterfeit KYC documents, or fraudulent Proof of Performance (POP) photos.
* Circumvent the platform to complete off-platform transactions after discovering counterparties on Viskotu.
* Upload ad creative content that is defamatory, illegal, infringing on third-party intellectual property, or violates local advertising regulations.
* Interfere with or disrupt the security, servers, or networks connected to the platform.

---

## 7. Limitation of Liability

To the maximum extent permitted by applicable law, Viskotu and its affiliates, officers, employees, and agents shall not be liable for any indirect, incidental, special, consequential, or punitive damages arising out of your use of the platform, physical ad damages, or third-party disputes between Advertisers, Space Owners, and Printers.

---

## 8. Amendments & Termination

We reserve the right to modify these Terms at any time. We will notify users of material changes via platform banner or email notification. Continued use of the platform after effective modifications constitutes acceptance of the revised Terms. Viskotu reserves the right to suspend or terminate accounts that violate these Terms or our SLA standards.

---

## 9. Governing Law & Dispute Resolution

These Terms shall be governed by and construed in accordance with applicable commercial laws. Any disputes arising between users regarding campaign execution shall first undergo Viskotu's internal Dispute Resolution and Support mediation before initiating external legal proceedings.
"""


class SiteSettings(models.Model):
    """
    Singleton model to store platform-wide settings such as Privacy Policy
    and Terms of Service.
    """
    privacy_policy = models.TextField(blank=True, default=DEFAULT_PRIVACY_POLICY)
    terms_of_service = models.TextField(blank=True, default=DEFAULT_TERMS_OF_SERVICE)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return f"Site Settings (Updated: {self.updated_at.strftime('%Y-%m-%d %H:%M')})"

    @classmethod
    def load(cls):
        """
        Load or create the singleton instance with id=1.
        """
        obj, _ = cls.objects.get_or_create(id=1)
        return obj


import uuid
from django.conf import settings

class SupportTicket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='open')
    priority = models.CharField(max_length=50, default='medium')
    category = models.CharField(max_length=100, default='general')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ticket {self.id} - {self.subject}"


class SLAEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    related_entity_id = models.CharField(max_length=255)
    entity_type = models.CharField(max_length=50) # 'print_job', 'installation', etc
    event_type = models.CharField(max_length=50) # 'deadline_missed', 'quality_issue'
    severity = models.CharField(max_length=50, default='warning')
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"SLA Event {self.event_type} - {self.severity}"


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='taxonomy/categories/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class ItemType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='item_types')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class SurfaceMaterial(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

class PointOfInterest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    lat = models.FloatField()
    lng = models.FloatField()
    
    class Meta:
        db_table = 'points_of_interest'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.category})"


class AbstractTaxonomyModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    value = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=100)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ['sort_order', 'label']

    def __str__(self):
        return self.label


class CompanySize(AbstractTaxonomyModel):
    class Meta(AbstractTaxonomyModel.Meta):
        verbose_name_plural = 'Company Sizes'


class Industry(AbstractTaxonomyModel):
    class Meta(AbstractTaxonomyModel.Meta):
        verbose_name_plural = 'Industries'


class MonthlyBudget(AbstractTaxonomyModel):
    pass


class PrimaryGoal(AbstractTaxonomyModel):
    pass


class PrinterCapacity(AbstractTaxonomyModel):
    class Meta(AbstractTaxonomyModel.Meta):
        verbose_name_plural = 'Printer Capacities'


class SpaceCount(AbstractTaxonomyModel):
    pass


class Orientation(AbstractTaxonomyModel):
    pass


class PhysicalShape(AbstractTaxonomyModel):
    class Meta(AbstractTaxonomyModel.Meta):
        verbose_name_plural = 'Physical Shapes'


class QualityStandard(AbstractTaxonomyModel):
    class Meta(AbstractTaxonomyModel.Meta):
        verbose_name_plural = 'Quality Standards'


class AudienceBehavior(AbstractTaxonomyModel):
    class Meta(AbstractTaxonomyModel.Meta):
        verbose_name_plural = 'Audience Behaviors'


class TrafficDensity(AbstractTaxonomyModel):
    class Meta(AbstractTaxonomyModel.Meta):
        verbose_name_plural = 'Traffic Densities'


class PeakExposure(AbstractTaxonomyModel):
    class Meta(AbstractTaxonomyModel.Meta):
        verbose_name_plural = 'Peak Exposures'


class BillingPeriod(AbstractTaxonomyModel):
    class Meta(AbstractTaxonomyModel.Meta):
        verbose_name_plural = 'Billing Periods'

