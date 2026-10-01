"""Name pools for synthetic file listings. File names and owners are invented."""

# file type -> (extension, base names)
TYPES = {
    "report": ("pdf", ("Q3 sales report", "Annual impact report", "Site visit report", "Audit summary report",
                       "Market research report", "Incident report", "Weekly status report", "Usability test report",
                       "Field trial report", "Energy use report", "Board progress report", "Vendor review report")),
    "invoice": ("pdf", ("Invoice 4471", "Invoice 5120", "Invoice 3388", "Invoice 6012", "Invoice 2795",
                        "Invoice 7304", "Invoice 1186", "Invoice 8840", "Invoice 9157", "Invoice 4023",
                        "Invoice 5561", "Invoice 6679")),
    "slides": ("pptx", ("Launch plan deck", "All-hands slides", "Investor update deck", "Training deck",
                        "Roadmap review slides", "Kickoff deck", "Hiring pitch slides", "Partner briefing deck",
                        "Design crit slides", "Offsite agenda deck", "Customer demo slides", "Strategy deck")),
    "spreadsheet": ("xlsx", ("Budget tracker", "Headcount plan", "Expense sheet", "Inventory count", "Price list",
                             "Leads pipeline", "Shift roster", "Survey responses", "Travel costs", "Grant budget",
                             "Asset register", "Vendor scores")),
    "contract": ("docx", ("Office lease agreement", "Supplier contract", "Consulting agreement", "NDA with Northwind",
                          "Service level agreement", "Freelancer contract", "Licence agreement", "Rental contract",
                          "Partnership agreement", "Maintenance contract", "Data sharing agreement",
                          "Employment offer")),
}

OWNERS = ("me", "Priya Sharma", "Karthik Nair", "Emily Carter", "Chen Wei", "Grace Kim", "Kenji Sato", "Laura Schmidt")

RECIPIENTS = ("rahul@example.com", "divya@example.com", "finance@example.com", "kenji@example.com",
              "laura@example.com")
