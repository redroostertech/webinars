from flask import render_template


class DashboardController:
    """Handles HTTP concerns for dashboard pages. Delegates data to DataService."""

    def __init__(self, data_service):
        self._data = data_service

    def dashboard_page(self):
        metrics = self._data.compute_dashboard_metrics()
        return render_template("dashboard.html", metrics=metrics)

    def leads_page(self):
        leads = self._data.get_leads()
        metrics = self._data.compute_leads_metrics()
        return render_template("leads.html", leads=leads, metrics=metrics)

    def invoices_page(self):
        invoices = self._data.get_invoices()
        metrics = self._data.compute_invoices_metrics()
        return render_template("invoices.html", invoices=invoices, metrics=metrics)

    def projects_page(self):
        projects = self._data.get_projects()
        leads = self._data.get_leads()
        invoices = self._data.get_invoices()
        metrics = self._data.compute_projects_metrics()
        return render_template(
            "projects.html",
            projects=projects,
            leads=leads,
            invoices=invoices,
            metrics=metrics,
        )
