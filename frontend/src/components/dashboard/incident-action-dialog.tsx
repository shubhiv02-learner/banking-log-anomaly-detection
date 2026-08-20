import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import {
  api,
  type DashboardUser,
  type IncidentAction,
} from "@/lib/api/client";
import { SERVICE_LABELS } from "@/lib/api/placeholder-data";
import type { Ticket } from "@/lib/api/types";

const MIN_REMARKS_LEN = 5;

const TITLES: Record<IncidentAction, string> = {
  ASSIGNED: "Assign incident",
  RESOLVED: "Resolve incident",
  CLOSED: "Close incident",
};

const CONFIRM: Record<IncidentAction, string> = {
  ASSIGNED: "Assign",
  RESOLVED: "Resolve",
  CLOSED: "Close",
};

type IncidentActionDialogProps = {
  ticket: Ticket | null;
  action: IncidentAction | null;
  users: DashboardUser[];
  currentUserName: string;
  onClose: () => void;
  onSuccess: () => void;
};

export function IncidentActionDialog({
  ticket,
  action,
  users,
  currentUserName,
  onClose,
  onSuccess,
}: IncidentActionDialogProps) {
  const open = ticket !== null && action !== null;
  const [assignee, setAssignee] = useState("");
  const [remarks, setRemarks] = useState("");
  const [closureRemark, setClosureRemark] = useState("");
  const [preventiveAction, setPreventiveAction] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const defaultAssignee = useMemo(() => {
    const match = users.find(
      (user) => user.name.toLowerCase() === currentUserName.toLowerCase(),
    );
    return match?.name ?? users[0]?.name ?? "";
  }, [users, currentUserName]);

  useEffect(() => {
    if (!open) return;
    setAssignee(defaultAssignee);
    setRemarks("");
    setClosureRemark("");
    setPreventiveAction("");
    setError(null);
    setSubmitting(false);
  }, [open, ticket?.ticket_id, action, defaultAssignee]);

  async function onSubmit() {
    if (!ticket || !action || submitting) return;
    const clientError = validate();
    if (clientError) {
      setError(clientError);
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const result = await api.updateIncident({
        ticket_id: ticket.ticket_id,
        action,
        assigned_to: action === "ASSIGNED" ? assignee : undefined,
        remarks: action === "RESOLVED" ? remarks.trim() : action === "ASSIGNED" ? remarks.trim() || undefined : undefined,
        closure_remark: action === "CLOSED" ? closureRemark.trim() : undefined,
        preventive_action: action === "CLOSED" ? preventiveAction.trim() : undefined,
      });
      toast.success(result.message);
      onSuccess();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Update failed");
    } finally {
      setSubmitting(false);
    }
  }

  function validate(): string | null {
    if (!action) return "Select an action.";
    if (action === "ASSIGNED") {
      if (!assignee.trim()) return "Select an assignee.";
      return null;
    }
    if (action === "RESOLVED") {
      if (remarks.trim().length < MIN_REMARKS_LEN) {
        return `Resolution remarks must be at least ${MIN_REMARKS_LEN} characters.`;
      }
      return null;
    }
    if (closureRemark.trim().length < MIN_REMARKS_LEN) {
      return `Closure remark must be at least ${MIN_REMARKS_LEN} characters.`;
    }
    if (preventiveAction.trim().length < MIN_REMARKS_LEN) {
      return `Preventive action must be at least ${MIN_REMARKS_LEN} characters.`;
    }
    return null;
  }

  return (
    <Dialog open={open} onOpenChange={(next) => !next && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{action ? TITLES[action] : "Update incident"}</DialogTitle>
          <DialogDescription>
            {ticket
              ? `${ticket.ticket_id} · ${SERVICE_LABELS[ticket.service] ?? ticket.service} · ${ticket.status}`
              : ""}
            {action === "CLOSED"
              ? " Incident must be resolved before it can be closed."
              : null}
          </DialogDescription>
        </DialogHeader>

        {action === "ASSIGNED" ? (
          <div className="space-y-3">
            <div className="space-y-2">
              <Label htmlFor="assignee">Assignee</Label>
              <Select value={assignee} onValueChange={setAssignee}>
                <SelectTrigger id="assignee" className="w-full">
                  <SelectValue placeholder="Select assignee" />
                </SelectTrigger>
                <SelectContent>
                  {users.length === 0 ? (
                    <SelectItem value="__none" disabled>
                      No active users
                    </SelectItem>
                  ) : (
                    users.map((user) => (
                      <SelectItem key={user.user_id} value={user.name}>
                        {user.name}
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="assign-remarks">Remarks (optional)</Label>
              <Textarea
                id="assign-remarks"
                value={remarks}
                onChange={(event) => setRemarks(event.target.value)}
                rows={3}
              />
            </div>
          </div>
        ) : null}

        {action === "RESOLVED" ? (
          <div className="space-y-2">
            <Label htmlFor="resolve-remarks">Resolution remarks *</Label>
            <Textarea
              id="resolve-remarks"
              value={remarks}
              onChange={(event) => setRemarks(event.target.value)}
              rows={4}
              required
            />
          </div>
        ) : null}

        {action === "CLOSED" ? (
          <div className="space-y-3">
            <div className="space-y-2">
              <Label htmlFor="closure-remark">Closure remark *</Label>
              <Textarea
                id="closure-remark"
                value={closureRemark}
                onChange={(event) => setClosureRemark(event.target.value)}
                rows={3}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="preventive-action">Preventive action *</Label>
              <Textarea
                id="preventive-action"
                value={preventiveAction}
                onChange={(event) => setPreventiveAction(event.target.value)}
                rows={3}
                required
              />
            </div>
          </div>
        ) : null}

        {error ? <p className="text-sm text-destructive">{error}</p> : null}

        <DialogFooter>
          <Button type="button" variant="outline" onClick={onClose} disabled={submitting}>
            Cancel
          </Button>
          <Button type="button" onClick={() => void onSubmit()} disabled={submitting}>
            {submitting ? "Saving…" : action ? CONFIRM[action] : "Save"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
