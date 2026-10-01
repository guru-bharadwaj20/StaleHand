"""Word pools for synthetic inboxes. Names and topics are invented; any match to a real person is chance."""

SENDERS = (
    "Priya Sharma", "Rahul Verma", "Ananya Iyer", "Karthik Nair", "Meera Pillai", "Arjun Reddy", "Sneha Kulkarni",
    "Vikram Rao", "Divya Menon", "Rohan Gupta", "Emily Carter", "James Walker", "Sofia Martinez", "Liam O'Brien",
    "Chen Wei", "Yuki Tanaka", "Fatima Khan", "Omar Haddad", "Grace Kim", "Lucas Silva", "Hannah Mueller",
    "Noah Johnson", "Aisha Bello", "Mateo Rossi", "Olivia Brown", "Daniel Cohen", "Zara Ahmed", "Ethan Park",
    "Isabella Costa", "Ravi Shankar", "Nisha Patel", "Tom Fischer", "Laura Schmidt", "Kenji Sato", "Amara Okafor",
    "Leo Dubois", "Maya Singh", "Samuel Lee", "Chloe Martin", "Aditya Joshi",
)

# (short topic used in task text, subject line shown in the inbox)
TOPICS = (
    ("venue booking", "Venue booking for the offsite"), ("Q3 budget", "Q3 budget draft for review"),
    ("invoice", "Invoice #4471 for September"), ("contract renewal", "Contract renewal terms"),
    ("design review", "Design review notes"), ("onboarding plan", "Onboarding plan for new hires"),
    ("travel itinerary", "Travel itinerary for the Pune trip"), ("server outage", "Server outage postmortem"),
    ("hiring panel", "Hiring panel schedule"), ("quarterly report", "Quarterly report figures"),
    ("team lunch", "Team lunch on Friday"), ("launch checklist", "Launch checklist v2"),
    ("expense claim", "Expense claim approval"), ("client feedback", "Client feedback on the mockups"),
    ("security audit", "Security audit findings"), ("vendor quote", "Vendor quote for laptops"),
    ("sprint retro", "Sprint retro action items"), ("conference talk", "Conference talk proposal"),
    ("office move", "Office move logistics"), ("training session", "Training session slides"),
    ("tax documents", "Tax documents for filing"), ("project timeline", "Project timeline update"),
    ("data migration", "Data migration plan"), ("performance review", "Performance review schedule"),
    ("newsletter copy", "Marketing copy for the newsletter"), ("API key rotation", "API key rotation next week"),
    ("board meeting", "Board meeting agenda"), ("customer survey", "Customer survey results"),
    ("insurance claim", "Insurance claim status"), ("research proposal", "Research proposal draft"),
    ("lab safety refresher", "Lab safety refresher"), ("parking permit", "Parking permit renewal"),
    ("holiday calendar", "Holiday calendar 2027"), ("release notes", "Release notes for 3.2"),
    ("user interviews", "User interviews recap"), ("pricing page", "Pricing page changes"),
    ("bug bash", "Bug bash sign-up"), ("workshop registration", "Workshop registration confirmed"),
    ("shipping delay", "Shipping delay on order 88213"), ("thesis draft", "Thesis draft, chapter 3"),
    ("grant application", "Grant application checklist"), ("cab reimbursement", "Reimbursement for cab fares"),
    ("fire drill", "Fire drill on Tuesday"), ("Wi-Fi upgrade", "Wi-Fi upgrade this weekend"),
    ("course feedback", "Course feedback form"), ("partnership proposal", "Partnership proposal from Northwind"),
    ("demo recording", "Demo recording link"), ("rent agreement", "Rent agreement copy"),
    ("code review", "Code review for PR 412"), ("webinar invite", "Webinar invite: AI in retail"),
)

SNIPPETS = (
    "Hi, sharing the details below.", "Please take a look when you get a chance.", "Quick update on this.",
    "Let me know if anything is missing.", "Attached for your reference.", "Following up on our call earlier.",
    "Can you confirm by end of day?", "Thanks for the quick turnaround.", "Adding a few notes from my side.",
    "See the summary in the attachment.",
)

RECIPIENTS = ("rahul@example.com", "divya@example.com", "finance@example.com", "kenji@example.com",
              "laura@example.com")
