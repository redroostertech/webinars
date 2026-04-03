"""Read from Sheets and compute dashboard metrics. No local cache."""

import json
import os
from datetime import datetime, timedelta

import config
from models import Lead, Invoice, Project


class DataService:

    def __init__(self, sheets_service):
        self._sheets = sheets_service
        self._use_sample = not config.MASTER_SHEET_ID

    def _read_sample(self, filename):
        """Read sample data from a local JSON file."""
        path = os.path.join(config.SAMPLE_DATA_DIR, filename)
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def _read_as_dicts(self, tab_name):
        """Read a sheet tab and return list of dicts."""
        try:
            headers, rows = self._sheets.read_tab(tab_name)
        except Exception:
            return []
        results = []
        for row in rows:
            record = {}
            for i, h in enumerate(headers):
                record[h] = row[i] if i < len(row) else ""
            results.append(record)
        return results

    def get_leads(self):
        if self._use_sample:
            raw = self._read_sample("leads.json")
        else:
            raw = self._read_as_dicts("Leads")
        return [Lead.from_dict(d) for d in raw]

    def get_invoices(self):
        if self._use_sample:
            raw = self._read_sample("invoices.json")
        else:
            raw = self._read_as_dicts("Invoices")
        return [Invoice.from_dict(d) for d in raw]

    def get_projects(self):
        """Read projects from Google Sheet if configured, otherwise local JSON."""
        if config.PROJECTS_SHEET_ID:
            try:
                raw = self._read_projects_from_sheet()
                self._cache_projects_locally(raw)
                return [Project.from_dict(d) for d in raw]
            except Exception:
                pass
        # Fallback to local JSON
        return [Project.from_dict(d) for d in self._read_projects_local()]

    def _read_projects_from_sheet(self):
        """Read project rows from the projects Google Sheet."""
        headers, rows = self._sheets.read_tab_from_sheet(
            config.PROJECTS_SHEET_ID, "Sheet1"
        )
        results = []
        for row in rows:
            record = {}
            for i, h in enumerate(headers):
                record[h] = row[i] if i < len(row) else ""
            results.append(record)
        return results

    def _read_projects_local(self):
        projects_path = os.path.join(config.DATA_DIR, "projects", "projects.json")
        try:
            with open(projects_path, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def _cache_projects_locally(self, raw):
        """Write a local cache of projects for offline use."""
        projects_path = os.path.join(config.DATA_DIR, "projects", "projects.json")
        os.makedirs(os.path.dirname(projects_path), exist_ok=True)
        with open(projects_path, "w") as f:
            json.dump(raw, f, indent=4)

    def get_all_data(self):
        return {
            "leads": self.get_leads(),
            "invoices": self.get_invoices(),
            "projects": self.get_projects(),
        }

    def compute_dashboard_metrics(self):
        """Compute high-level metrics for the main dashboard."""
        leads = self.get_leads()
        invoices = self.get_invoices()
        projects = self.get_projects()

        # Total leads with stage breakdown
        total_leads = len(leads)
        leads_by_stage = {}
        for lead in leads:
            stage = lead.stage or "unknown"
            leads_by_stage[stage] = leads_by_stage.get(stage, 0) + 1

        # Outstanding invoices
        outstanding = [
            inv for inv in invoices
            if inv.status in ("sent", "draft", "overdue")
        ]
        outstanding_amount = sum(
            _safe_float(inv.amount) for inv in outstanding
        )

        # Active projects
        active_projects = [p for p in projects if p.status == "active"]

        # Revenue this month (paid invoices)
        monthly_revenue = sum(
            _safe_float(inv.amount)
            for inv in invoices if inv.status == "paid"
        )

        # Recent activity (last 10 items from all objects by date)
        activity = []
        for lead in leads:
            activity.append({
                "type": "lead",
                "description": (
                    f"Lead: {lead.name or 'Unknown'} "
                    f"({lead.company})"
                ),
                "date": lead.created_at,
                "stage": lead.stage,
            })
        for inv in invoices:
            activity.append({
                "type": "invoice",
                "description": (
                    f"Invoice {inv.invoice_number}: "
                    f"${_safe_float(inv.amount):,.0f}"
                ),
                "date": inv.due_date,
                "status": inv.status,
            })
        for proj in projects:
            activity.append({
                "type": "project",
                "description": (
                    f"Project: {proj.name} "
                    f"({proj.client})"
                ),
                "date": proj.deadline,
                "status": proj.status,
            })
        activity.sort(key=lambda x: x.get("date", ""), reverse=True)

        # Revenue chart data — group paid invoices by month
        revenue_by_month = {}
        for inv in invoices:
            if inv.status == "paid":
                date_str = inv.due_date or ""
                if len(date_str) >= 7:
                    month_key = date_str[:7]
                    revenue_by_month[month_key] = (
                        revenue_by_month.get(month_key, 0)
                        + _safe_float(inv.amount)
                    )
        chart_labels = sorted(revenue_by_month.keys())
        chart_values = [revenue_by_month[k] for k in chart_labels]

        return {
            "total_leads": total_leads,
            "leads_by_stage": leads_by_stage,
            "outstanding_invoices": len(outstanding),
            "outstanding_amount": outstanding_amount,
            "active_projects": len(active_projects),
            "monthly_revenue": monthly_revenue,
            "recent_activity": activity[:10],
            "chart_labels": chart_labels,
            "chart_values": chart_values,
        }

    def compute_leads_metrics(self):
        """Metrics for the leads page."""
        leads = self.get_leads()
        total = len(leads)
        by_stage = {}
        for lead in leads:
            stage = lead.stage or "unknown"
            by_stage[stage] = by_stage.get(stage, 0) + 1

        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        new_this_week = sum(
            1 for lead in leads
            if (lead.created_at or "") >= week_ago
        )

        return {
            "total": total,
            "new_this_week": new_this_week,
            "new": by_stage.get("new", 0),
            "contacted": by_stage.get("contacted", 0),
            "converted": by_stage.get("converted", 0),
        }

    def compute_invoices_metrics(self):
        """Metrics for the invoices page."""
        invoices = self.get_invoices()
        total_invoiced = sum(
            _safe_float(inv.amount) for inv in invoices
        )
        total_paid = sum(
            _safe_float(inv.amount)
            for inv in invoices if inv.status == "paid"
        )
        total_outstanding = sum(
            _safe_float(inv.amount)
            for inv in invoices
            if inv.status in ("sent", "draft", "overdue")
        )
        overdue_count = sum(
            1 for inv in invoices if inv.status == "overdue"
        )

        return {
            "total_invoiced": total_invoiced,
            "total_paid": total_paid,
            "total_outstanding": total_outstanding,
            "overdue_count": overdue_count,
            "total_count": len(invoices),
        }

    def compute_projects_metrics(self):
        """Metrics for the projects page."""
        projects = self.get_projects()
        active = [p for p in projects if p.status == "active"]
        total_budget = sum(
            _safe_float(p.budget) for p in projects
        )
        total_billed = sum(
            _safe_float(p.total_billed) for p in projects
        )
        utilization = (
            (total_billed / total_budget * 100) if total_budget > 0 else 0
        )

        return {
            "active_count": len(active),
            "total_count": len(projects),
            "total_budget": total_budget,
            "total_billed": total_billed,
            "utilization": round(utilization, 1),
        }


    def save_invoices(self, invoice_dicts):
        """Overwrite all invoices with the given list of dicts."""
        if self._use_sample:
            path = os.path.join(config.SAMPLE_DATA_DIR, "invoices.json")
            with open(path, "w") as f:
                json.dump(invoice_dicts, f, indent=4)
        else:
            if not invoice_dicts:
                return {"status": "success", "message": "No invoices to save"}
            headers = list(invoice_dicts[0].keys())
            rows = [headers]
            for record in invoice_dicts:
                rows.append([str(record.get(h, "")) for h in headers])
            self._sheets.write_tab("Invoices", rows)
        return {"status": "success", "message": f"Saved {len(invoice_dicts)} invoices"}

    def update_record(self, object_type, index, updates):
        """Update a record by index. Projects always write to local JSON."""
        if object_type == "projects":
            return self._update_project_record(index, updates)

        file_map = {"leads": "leads.json", "invoices": "invoices.json"}
        tab_map = {"leads": "Leads", "invoices": "Invoices"}

        if self._use_sample:
            path = os.path.join(config.SAMPLE_DATA_DIR, file_map[object_type])
            with open(path, "r") as f:
                records = json.load(f)
            if index < 0 or index >= len(records):
                return {"status": "error", "message": "Record not found"}
            records[index].update(updates)
            with open(path, "w") as f:
                json.dump(records, f, indent=4)
        else:
            tab = tab_map[object_type]
            headers, rows = self._sheets.read_tab(tab)
            if index < 0 or index >= len(rows):
                return {"status": "error", "message": "Record not found"}
            for key, value in updates.items():
                if key in headers:
                    col_idx = headers.index(key)
                    while len(rows[index]) <= col_idx:
                        rows[index].append("")
                    rows[index][col_idx] = str(value)
            all_rows = [headers] + rows
            self._sheets.write_tab(tab, all_rows)

        return {"status": "success", "message": f"{object_type[:-1].title()} updated"}

    def _update_project_record(self, index, updates):
        """Update project locally and sync back to Google Sheet if configured."""
        # Update local JSON
        projects_path = os.path.join(config.DATA_DIR, "projects", "projects.json")
        try:
            with open(projects_path, "r") as f:
                records = json.load(f)
        except Exception:
            return {"status": "error", "message": "Projects file not found"}
        if index < 0 or index >= len(records):
            return {"status": "error", "message": "Project not found"}
        records[index].update(updates)
        with open(projects_path, "w") as f:
            json.dump(records, f, indent=4)

        # Sync back to Google Sheet if configured
        if config.PROJECTS_SHEET_ID:
            try:
                headers = list(records[0].keys())
                rows = [headers]
                for record in records:
                    rows.append([str(record.get(h, "")) for h in headers])
                self._sheets.write_tab_to_sheet(
                    config.PROJECTS_SHEET_ID, "Sheet1", rows
                )
            except Exception:
                pass  # Local update succeeded, sheet sync is best-effort

        return {"status": "success", "message": "Project updated"}


def _safe_float(value):
    """Convert a value to float, returning 0 on failure."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0
