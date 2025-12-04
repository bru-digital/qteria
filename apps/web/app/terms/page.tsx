import { Metadata } from "next"
import Link from "next/link"

// Terms of Service Configuration
const LAST_UPDATED_DATE = "December 4, 2025"

export const metadata: Metadata = {
  title: "Terms of Service | Qteria",
  description: "Terms of Service for Qteria AI-powered document validation platform",
}

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container max-w-4xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/"
            className="text-blue-500 hover:text-blue-600 font-medium mb-4 inline-block"
          >
            ← Back to Home
          </Link>
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">Terms of Service</h1>
          <p className="text-sm text-gray-600">Last updated: {LAST_UPDATED_DATE}</p>
        </div>

        {/* Content */}
        <div className="bg-white rounded-lg shadow-sm p-6 md:p-8 space-y-8 print:shadow-none">

          {/* Introduction */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. Service Description</h2>
            <p className="text-base text-gray-700 leading-relaxed">
              Qteria (&quot;we&quot;, &quot;us&quot;, &quot;our&quot;) provides an AI-powered document validation platform designed for Testing, Inspection, and Certification (TIC) organizations. The Service enables you to create validation workflows, upload documents, and receive evidence-based AI assessments.
            </p>
            <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 mt-4">
              <p className="text-base text-gray-800 leading-relaxed font-semibold">
                IMPORTANT: Qteria provides pre-assessment validation only. AI results are not final certification decisions. Final certification must be performed by qualified professionals.
              </p>
            </div>
          </section>

          {/* Subscription & Payment */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. Subscription and Payment</h2>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">2.1 Pricing Tiers</h3>
            <ul className="list-disc list-inside space-y-2 text-gray-700 mb-4 ml-4">
              <li><strong>Professional Tier:</strong> $30,000/year (flat fee, unlimited assessments)</li>
              <li><strong>Enterprise Tier:</strong> Custom pricing for custom features and integrations</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">2.2 Payment Terms</h3>
            <ul className="list-disc list-inside space-y-2 text-gray-700 mb-4 ml-4">
              <li>Annual prepayment required (invoice or credit card)</li>
              <li>Subscriptions auto-renew unless canceled 30 days before renewal date</li>
              <li>Payment due within 30 days of invoice date</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">2.3 Refund Policy</h3>
            <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
              <li><strong>30-Day Satisfaction Guarantee:</strong> Pro-rata refund if canceled within first 30 days</li>
              <li><strong>No Mid-Year Cancellation:</strong> No refunds after 30 days (annual commitment applies)</li>
              <li>Outstanding fees remain due upon termination</li>
            </ul>
          </section>

          {/* User Accounts & Responsibilities */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. User Accounts and Responsibilities</h2>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              By using Qteria, you agree to:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
              <li>Keep your account credentials secure and confidential</li>
              <li>Not share login credentials with unauthorized users</li>
              <li>Take responsibility for all activity under your account</li>
              <li>Ensure you have authorization to upload documents to the platform</li>
              <li>Notify us immediately of any unauthorized access or security breach</li>
            </ul>
            <p className="text-base text-gray-700 leading-relaxed mt-4">
              Organization administrators are responsible for managing user accounts (Process Managers, Project Handlers) and ensuring compliance with these Terms.
            </p>
          </section>

          {/* Acceptable Use Policy */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. Acceptable Use Policy</h2>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">4.1 Permitted Use</h3>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              You may use Qteria for document validation related to certification and compliance workflows as intended by the platform.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">4.2 Prohibited Activities</h3>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              You may NOT:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700 mb-4 ml-4">
              <li>Upload malware, viruses, or malicious code</li>
              <li>Attempt to reverse-engineer AI models or algorithms</li>
              <li>Make excessive API requests intended to disrupt service (abuse/DoS)</li>
              <li>Upload content violating third-party intellectual property rights</li>
              <li>Use the service for illegal activities</li>
              <li>Scrape or extract data beyond normal use and API limits</li>
              <li>Resell or redistribute access to the platform without authorization</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">4.3 Consequences of Violation</h3>
            <p className="text-base text-gray-700 leading-relaxed">
              Violation of this policy may result in account suspension or termination without refund, at our sole discretion.
            </p>
          </section>

          {/* Data Ownership & IP */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. Data Ownership and Intellectual Property</h2>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">5.1 Customer Data</h3>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              You retain ownership of all uploaded documents, workflow definitions, and assessment results. We claim no ownership rights over your content.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">5.2 Qteria Intellectual Property</h3>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              Qteria owns all rights to the platform code, AI models, algorithms, design, and branding. These Terms do not grant you any ownership or license to our intellectual property beyond the right to use the Service.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">5.3 Limited License</h3>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              You grant Qteria a limited, non-exclusive license to process your documents for the sole purpose of providing validation services. This license terminates when you delete documents or close your account.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">5.4 Zero AI Training</h3>
            <div className="bg-blue-50 border-l-4 border-blue-500 p-4">
              <p className="text-base text-gray-800 leading-relaxed">
                <strong>Important:</strong> We will NOT use your documents to train AI models. We maintain zero-retention agreements with our AI providers (Anthropic Claude). Your documents are processed ephemally and never stored by our AI vendors.
              </p>
            </div>

            <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">5.5 Feedback and Feature Requests</h3>
            <p className="text-base text-gray-700 leading-relaxed">
              Any feedback, suggestions, or feature requests you provide become the property of Qteria and may be used to improve the Service without compensation to you.
            </p>
          </section>

          {/* Service Levels & Availability */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">6. Service Level Agreement (SLA)</h2>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">6.1 Uptime Commitment</h3>
            <ul className="list-disc list-inside space-y-2 text-gray-700 mb-4 ml-4">
              <li><strong>Target Uptime:</strong> 99.5% monthly uptime (approximately 3.6 hours of allowed downtime per month)</li>
              <li><strong>Planned Maintenance:</strong> Announced at least 48 hours in advance, scheduled during low-usage windows</li>
              <li><strong>Emergency Maintenance:</strong> May occur without notice for critical security issues</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">6.2 AI Processing Performance</h3>
            <ul className="list-disc list-inside space-y-2 text-gray-700 mb-4 ml-4">
              <li><strong>Target Processing Time:</strong> P95 &lt;10 minutes for typical assessments</li>
              <li><strong>Best-Effort Basis:</strong> Processing times are targets, not guarantees</li>
              <li>Actual processing time depends on document size, complexity, and criteria count</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">6.3 Support Response Times</h3>
            <ul className="list-disc list-inside space-y-2 text-gray-700 mb-4 ml-4">
              <li><strong>Critical Issues</strong> (service down): &lt;4 hours response time</li>
              <li><strong>High Priority</strong> (feature broken): &lt;24 hours response time</li>
              <li><strong>Normal Priority</strong> (general inquiries): &lt;48 hours response time</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">6.4 SLA Credits</h3>
            <p className="text-base text-gray-700 leading-relaxed">
              If monthly uptime falls below 99.5%, you will receive a 10% monthly credit on your next invoice. SLA credits are your sole remedy for service downtime.
            </p>
          </section>

          {/* Data Security & Privacy */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. Data Security and Privacy</h2>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              For detailed information about data handling, please refer to our <Link href="/privacy" className="text-blue-500 hover:underline">Privacy Policy</Link>. Key security measures include:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700 mb-4 ml-4">
              <li><strong>Encryption at Rest:</strong> AES-256 encryption for stored documents</li>
              <li><strong>Encryption in Transit:</strong> TLS 1.3 for all data transmission</li>
              <li><strong>Multi-Tenancy Isolation:</strong> Organization-level data separation</li>
              <li><strong>Role-Based Access Control:</strong> User permissions enforced at all levels</li>
              <li><strong>Audit Logging:</strong> Comprehensive tracking of all user actions</li>
              <li><strong>SOC2 Type II Certification:</strong> Target Q3 2026</li>
            </ul>
            <p className="text-base text-gray-700 leading-relaxed">
              You have the right to request annual security questionnaires and SOC2 reports once available.
            </p>
          </section>

          {/* Confidentiality */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">8. Confidentiality</h2>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              Both parties agree to keep confidential information private:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700 mb-4 ml-4">
              <li><strong>Your Confidential Information:</strong> All uploaded documents, workflow definitions, and assessment results</li>
              <li><strong>Our Confidential Information:</strong> Platform source code, AI models, algorithms, and business information</li>
            </ul>
            <p className="text-base text-gray-700 leading-relaxed">
              Confidentiality obligations survive termination of this agreement for 2 years.
            </p>
          </section>

          {/* Warranties & Disclaimers */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">9. Warranties and Disclaimers</h2>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">9.1 Service Warranty</h3>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              Qteria provides the Service with reasonable skill and care, consistent with industry standards for B2B SaaS platforms.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">9.2 Disclaimers</h3>
            <div className="bg-gray-50 border-l-4 border-gray-400 p-4 mb-4">
              <p className="text-base text-gray-800 leading-relaxed font-semibold mb-2">
                THE SERVICE IS PROVIDED &quot;AS IS&quot; WITHOUT WARRANTY OF ANY KIND. WE DISCLAIM ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING:
              </p>
              <ul className="list-disc list-inside space-y-1 text-gray-700 ml-4">
                <li>No guarantee of AI accuracy or freedom from errors</li>
                <li>No guarantee of uninterrupted or error-free operation</li>
                <li>No guarantee that the Service will meet all your requirements</li>
                <li>AI validation is pre-assessment only, not final certification</li>
              </ul>
            </div>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">9.3 Customer Responsibility</h3>
            <p className="text-base text-gray-700 leading-relaxed">
              You acknowledge that final certification decisions must be made by qualified professionals. Qteria is not liable for certification outcomes based on AI validation results.
            </p>
          </section>

          {/* Limitation of Liability */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">10. Limitation of Liability</h2>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">10.1 Liability Cap</h3>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              Qteria&apos;s total liability for any claims arising from these Terms or the Service is limited to the fees you paid in the 12 months prior to the claim.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">10.2 Exclusion of Consequential Damages</h3>
            <div className="bg-gray-50 border-l-4 border-gray-400 p-4 mb-4">
              <p className="text-base text-gray-800 leading-relaxed">
                TO THE MAXIMUM EXTENT PERMITTED BY LAW, QTERIA SHALL NOT BE LIABLE FOR INDIRECT, CONSEQUENTIAL, INCIDENTAL, SPECIAL, OR PUNITIVE DAMAGES, INCLUDING LOST PROFITS, LOST DATA, OR BUSINESS INTERRUPTION.
              </p>
            </div>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">10.3 Exceptions</h3>
            <p className="text-base text-gray-700 leading-relaxed">
              Nothing in these Terms limits liability for:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
              <li>Gross negligence or willful misconduct</li>
              <li>Data breach caused by Qteria&apos;s negligence</li>
              <li>Violations of applicable law that cannot be contractually limited</li>
            </ul>
          </section>

          {/* Termination */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">11. Termination</h2>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">11.1 Termination by Customer</h3>
            <ul className="list-disc list-inside space-y-2 text-gray-700 mb-4 ml-4">
              <li>Provide 30-day written notice before renewal date</li>
              <li>No mid-year cancellation without forfeiture of fees</li>
              <li>Access continues until end of prepaid period</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">11.2 Termination by Qteria</h3>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              We may terminate your account:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700 mb-4 ml-4">
              <li><strong>For Cause:</strong> Non-payment, breach of Terms, or illegal activity (15-day cure period provided)</li>
              <li><strong>Without Cause:</strong> With 90-day notice (we will provide exit assistance)</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">11.3 Effect of Termination</h3>
            <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
              <li>You must export your data within 30 days of termination</li>
              <li>We will delete your data 30 days after termination (except audit logs retained for 7 years)</li>
              <li>Outstanding fees remain due</li>
              <li>Termination does not relieve either party of obligations incurred before termination</li>
            </ul>
          </section>

          {/* Changes to Terms */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">12. Changes to Terms of Service</h2>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              We may update these Terms from time to time. We will notify you of material changes via email at least 30 days before they take effect.
            </p>
            <p className="text-base text-gray-700 leading-relaxed">
              Continued use of the Service after changes take effect constitutes acceptance of the updated Terms. If you disagree with changes, you may terminate your account before the changes take effect.
            </p>
          </section>

          {/* Governing Law */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">13. Governing Law and Dispute Resolution</h2>
            {/* TODO: [BLOCKS PRODUCTION] Specify governing law jurisdiction based on target market:
                - If EU-focused: Consider German law (friendly to B2B contracts) or jurisdiction where company is registered
                - If US-focused: Delaware or California law (standard for B2B SaaS)
                - Requires legal counsel review to determine appropriate jurisdiction */}

            <h3 className="text-xl font-semibold text-gray-800 mb-3">13.1 Governing Law</h3>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              These Terms are governed by the laws of [TO BE DETERMINED - requires legal counsel to specify jurisdiction based on company registration and target market].
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">13.2 Dispute Resolution</h3>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              In the event of a dispute:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700 mb-4 ml-4">
              <li>Both parties agree to attempt good faith negotiation for 30 days</li>
              <li>If negotiation fails, disputes will be resolved through binding arbitration or courts in [jurisdiction to be specified]</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">13.3 Jurisdiction</h3>
            <p className="text-base text-gray-700 leading-relaxed">
              You consent to the exclusive jurisdiction of courts in [TO BE DETERMINED] for any legal proceedings.
            </p>
          </section>

          {/* General Provisions */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">14. General Provisions</h2>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">14.1 Assignment</h3>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              You may not assign or transfer these Terms without our written consent. We may assign these Terms in connection with a merger, acquisition, or sale of assets.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">14.2 Force Majeure</h3>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              Neither party is liable for delays or failures due to events beyond reasonable control (natural disasters, wars, pandemics, government actions, internet outages, etc.).
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">14.3 Severability</h3>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              If any provision of these Terms is found invalid or unenforceable, the remaining provisions remain in full force and effect.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">14.4 Entire Agreement</h3>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              These Terms, together with our Privacy Policy, constitute the entire agreement between you and Qteria and supersede all prior agreements or understandings.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">14.5 No Third-Party Beneficiaries</h3>
            <p className="text-base text-gray-700 leading-relaxed">
              These Terms are solely between you and Qteria. No third party has rights under these Terms.
            </p>
          </section>

          {/* Contact */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">15. Contact Information</h2>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              For questions about these Terms of Service, please contact us:
            </p>
            <div className="bg-gray-50 p-4 rounded">
              <p className="text-base text-gray-800">
                <strong>Email:</strong> <a href="mailto:legal@qteria.com" className="text-blue-500 hover:underline">legal@qteria.com</a><br />
                <strong>Company:</strong> Qteria<br />
                {/* TODO: [BLOCKS PRODUCTION] Add full legal address:
                    - Street address
                    - City, Postal code
                    - Country
                    Required for legal enforceability and GDPR compliance */}
                <strong>Address:</strong> [TO BE DETERMINED - requires legal entity registration]
              </p>
            </div>
          </section>

        </div>

        {/* Footer Navigation */}
        <div className="mt-8 text-center space-y-2">
          <Link
            href="/"
            className="text-blue-500 hover:text-blue-600 font-medium inline-block"
          >
            ← Back to Home
          </Link>
          <span className="mx-3 text-gray-400">•</span>
          <Link
            href="/privacy"
            className="text-blue-500 hover:text-blue-600 font-medium inline-block"
          >
            Privacy Policy
          </Link>
        </div>
      </div>
    </div>
  )
}
