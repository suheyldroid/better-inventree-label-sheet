import React from "react";
import {
  ActionIcon,
  Alert,
  Button,
  Group,
  Modal,
  NumberInput,
  Stack,
  Switch,
  Table,
  Text,
  TextInput,
  Title,
  Tooltip,
} from "@mantine/core";
import {
  type InvenTreePluginContext,
  checkPluginVersion,
} from "@inventreedb/ui";
import { useCallback, useEffect, useMemo, useState } from "react";

/** A single paper size definition. */
interface PaperSize {
  display_name: string;
  width: number;
  height: number;
}

/** A single sheet layout definition, mirroring the backend SheetLayout. */
interface SheetLayout {
  display_name: string;
  page_size: PaperSize;
  label_width: number;
  label_height: number;
  columns: number;
  rows: number;
  column_spacing: number;
  row_spacing: number;
  corner_radius: number;
  spacing_top: number | null;
  spacing_left: number | null;
}

/** A layout paired with its code (the object key) for editing in the UI. */
interface LayoutEntry {
  code: string;
  layout: SheetLayout;
}

type LayoutMap = Record<string, SheetLayout>;

function emptyLayout(): SheetLayout {
  return {
    display_name: "",
    page_size: { display_name: "A4", width: 210, height: 297 },
    label_width: 50,
    label_height: 25,
    columns: 1,
    rows: 1,
    column_spacing: 0,
    row_spacing: 0,
    corner_radius: 0,
    spacing_top: null,
    spacing_left: null,
  };
}

function mapToEntries(map: LayoutMap): LayoutEntry[] {
  return Object.entries(map).map(([code, layout]) => ({ code, layout }));
}

function entriesToMap(entries: LayoutEntry[]): LayoutMap {
  const map: LayoutMap = {};
  for (const entry of entries) {
    map[entry.code] = entry.layout;
  }
  return map;
}

interface LayoutFormProps {
  initialCode: string;
  initialLayout: SheetLayout;
  existingCodes: string[];
  onCancel: () => void;
  onSave: (code: string, layout: SheetLayout) => void;
}

function LayoutForm({
  initialCode,
  initialLayout,
  existingCodes,
  onCancel,
  onSave,
}: LayoutFormProps) {
  const [code, setCode] = useState(initialCode);
  const [layout, setLayout] = useState<SheetLayout>(initialLayout);

  const update = useCallback((patch: Partial<SheetLayout>) => {
    setLayout((prev) => ({ ...prev, ...patch }));
  }, []);

  const updatePageSize = useCallback((patch: Partial<PaperSize>) => {
    setLayout((prev) => ({
      ...prev,
      page_size: { ...prev.page_size, ...patch },
    }));
  }, []);

  const codeError = useMemo(() => {
    if (!code.trim()) {
      return "Code is required";
    }
    if (code !== initialCode && existingCodes.includes(code)) {
      return "A layout with this code already exists";
    }
    return null;
  }, [code, initialCode, existingCodes]);

  const canSave = !codeError && layout.display_name.trim().length > 0;

  const num = (value: string | number): number => {
    const parsed = typeof value === "number" ? value : parseFloat(value);
    return Number.isFinite(parsed) ? parsed : 0;
  };

  return (
    <Stack gap="sm">
      <Group grow align="flex-start">
        <TextInput
          label="Layout code"
          description="Unique identifier (used in template metadata)"
          value={code}
          error={codeError}
          onChange={(e) => setCode(e.currentTarget.value)}
          required
        />
        <TextInput
          label="Display name"
          value={layout.display_name}
          onChange={(e) => update({ display_name: e.currentTarget.value })}
          required
        />
      </Group>

      <Title order={6}>Page</Title>
      <Group grow>
        <TextInput
          label="Paper name"
          value={layout.page_size.display_name}
          onChange={(e) =>
            updatePageSize({ display_name: e.currentTarget.value })
          }
        />
        <NumberInput
          label="Page width (mm)"
          value={layout.page_size.width}
          min={0}
          decimalScale={2}
          onChange={(v) => updatePageSize({ width: num(v) })}
        />
        <NumberInput
          label="Page height (mm)"
          value={layout.page_size.height}
          min={0}
          decimalScale={2}
          onChange={(v) => updatePageSize({ height: num(v) })}
        />
      </Group>

      <Title order={6}>Labels</Title>
      <Group grow>
        <NumberInput
          label="Label width (mm)"
          value={layout.label_width}
          min={0}
          decimalScale={2}
          onChange={(v) => update({ label_width: num(v) })}
        />
        <NumberInput
          label="Label height (mm)"
          value={layout.label_height}
          min={0}
          decimalScale={2}
          onChange={(v) => update({ label_height: num(v) })}
        />
        <NumberInput
          label="Corner radius (mm)"
          value={layout.corner_radius}
          min={0}
          decimalScale={2}
          onChange={(v) => update({ corner_radius: num(v) })}
        />
      </Group>
      <Group grow>
        <NumberInput
          label="Columns"
          value={layout.columns}
          min={1}
          allowDecimal={false}
          onChange={(v) => update({ columns: Math.max(1, Math.round(num(v))) })}
        />
        <NumberInput
          label="Rows"
          value={layout.rows}
          min={1}
          allowDecimal={false}
          onChange={(v) => update({ rows: Math.max(1, Math.round(num(v))) })}
        />
      </Group>

      <Title order={6}>Spacing</Title>
      <Group grow>
        <NumberInput
          label="Column spacing (mm)"
          value={layout.column_spacing}
          min={0}
          decimalScale={2}
          onChange={(v) => update({ column_spacing: num(v) })}
        />
        <NumberInput
          label="Row spacing (mm)"
          value={layout.row_spacing}
          min={0}
          decimalScale={2}
          onChange={(v) => update({ row_spacing: num(v) })}
        />
      </Group>

      <Switch
        label="Center labels automatically"
        description="When on, top/left margins are computed to center the grid on the page"
        checked={layout.spacing_top === null && layout.spacing_left === null}
        onChange={(e) => {
          if (e.currentTarget.checked) {
            update({ spacing_top: null, spacing_left: null });
          } else {
            update({ spacing_top: 0, spacing_left: 0 });
          }
        }}
      />
      {layout.spacing_top !== null || layout.spacing_left !== null ? (
        <Group grow>
          <NumberInput
            label="Top margin (mm)"
            value={layout.spacing_top ?? 0}
            min={0}
            decimalScale={2}
            onChange={(v) => update({ spacing_top: num(v) })}
          />
          <NumberInput
            label="Left margin (mm)"
            value={layout.spacing_left ?? 0}
            min={0}
            decimalScale={2}
            onChange={(v) => update({ spacing_left: num(v) })}
          />
        </Group>
      ) : null}

      <Group justify="flex-end" mt="md">
        <Button variant="default" onClick={onCancel}>
          Cancel
        </Button>
        <Button disabled={!canSave} onClick={() => onSave(code, layout)}>
          Save
        </Button>
      </Group>
    </Stack>
  );
}

function LayoutsPanel({ context }: { context: InvenTreePluginContext }) {
  const layoutsUrl = useMemo(() => {
    const url = context.context?.layouts_url;
    return typeof url === "string"
      ? url
      : "plugin/better-label-printer/layouts/";
  }, [context.context]);

  const [entries, setEntries] = useState<LayoutEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState<LayoutEntry | null>(null);
  const [isNew, setIsNew] = useState(false);

  const isSuperuser = !!context.user?.isSuperuser?.();

  const loadLayouts = useCallback(() => {
    setLoading(true);
    setError(null);
    context.api
      .get(layoutsUrl)
      .then((response: { data: LayoutMap }) => {
        setEntries(mapToEntries(response.data));
      })
      .catch((err: unknown) => {
        setError(`Failed to load layouts: ${describeError(err)}`);
      })
      .finally(() => setLoading(false));
  }, [context.api, layoutsUrl]);

  useEffect(() => {
    loadLayouts();
  }, [loadLayouts]);

  const persist = useCallback(
    (next: LayoutEntry[]) => {
      setSaving(true);
      setError(null);
      context.api
        .put(layoutsUrl, entriesToMap(next))
        .then((response: { data: LayoutMap }) => {
          setEntries(mapToEntries(response.data));
          showNotification(context, "Layouts saved", "green");
        })
        .catch((err: unknown) => {
          const message = describeError(err);
          setError(`Failed to save layouts: ${message}`);
          showNotification(context, `Save failed: ${message}`, "red");
          // Reload to stay consistent with the server state.
          loadLayouts();
        })
        .finally(() => setSaving(false));
    },
    [context, layoutsUrl, loadLayouts],
  );

  const handleSave = useCallback(
    (code: string, layout: SheetLayout) => {
      const editingCode = editing?.code;
      const next = entries.filter((entry) => entry.code !== editingCode);
      next.push({ code, layout });
      next.sort((a, b) => a.code.localeCompare(b.code));
      setEditing(null);
      persist(next);
    },
    [editing, entries, persist],
  );

  const handleDelete = useCallback(
    (code: string) => {
      if (entries.length <= 1) {
        setError("At least one layout is required.");
        return;
      }
      persist(entries.filter((entry) => entry.code !== code));
    },
    [entries, persist],
  );

  const rows = entries.map((entry) => {
    const l = entry.layout;
    return (
      <Table.Tr key={entry.code}>
        <Table.Td>{entry.code}</Table.Td>
        <Table.Td>{l.display_name}</Table.Td>
        <Table.Td>{l.page_size.display_name}</Table.Td>
        <Table.Td>
          {l.label_width} x {l.label_height} mm
        </Table.Td>
        <Table.Td>
          {l.columns} x {l.rows}
        </Table.Td>
        <Table.Td>
          {l.corner_radius > 0 ? `${l.corner_radius} mm` : "sharp"}
        </Table.Td>
        <Table.Td>
          <Group gap="xs" justify="flex-end" wrap="nowrap">
            <Tooltip label="Edit">
              <ActionIcon
                variant="subtle"
                disabled={!isSuperuser || saving}
                onClick={() => {
                  setIsNew(false);
                  setEditing(entry);
                }}
              >
                <EditIcon />
              </ActionIcon>
            </Tooltip>
            <Tooltip label="Delete">
              <ActionIcon
                variant="subtle"
                color="red"
                disabled={!isSuperuser || saving}
                onClick={() => handleDelete(entry.code)}
              >
                <DeleteIcon />
              </ActionIcon>
            </Tooltip>
          </Group>
        </Table.Td>
      </Table.Tr>
    );
  });

  return (
    <Stack gap="md">
      <Group justify="space-between">
        <div>
          <Title order={4}>Sheet Layouts</Title>
          <Text size="sm" c="dimmed">
            Define the paper sizes and label grids available when printing.
          </Text>
        </div>
        <Button
          disabled={!isSuperuser || saving || loading}
          onClick={() => {
            setIsNew(true);
            setEditing({ code: "", layout: emptyLayout() });
          }}
        >
          Add layout
        </Button>
      </Group>

      {!isSuperuser ? (
        <Alert color="yellow" title="Read only">
          Only administrators can edit sheet layouts.
        </Alert>
      ) : null}

      {error ? (
        <Alert
          color="red"
          title="Error"
          withCloseButton
          onClose={() => setError(null)}
        >
          {error}
        </Alert>
      ) : null}

      <Table striped highlightOnHover>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Code</Table.Th>
            <Table.Th>Name</Table.Th>
            <Table.Th>Paper</Table.Th>
            <Table.Th>Label size</Table.Th>
            <Table.Th>Grid</Table.Th>
            <Table.Th>Corners</Table.Th>
            <Table.Th />
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>{rows}</Table.Tbody>
      </Table>

      {!loading && entries.length === 0 ? (
        <Text c="dimmed" ta="center">
          No layouts defined yet.
        </Text>
      ) : null}

      <Modal
        opened={editing !== null}
        onClose={() => setEditing(null)}
        title={isNew ? "Add layout" : `Edit layout: ${editing?.code ?? ""}`}
        size="lg"
      >
        {editing ? (
          <LayoutForm
            initialCode={editing.code}
            initialLayout={editing.layout}
            existingCodes={entries.map((entry) => entry.code)}
            onCancel={() => setEditing(null)}
            onSave={handleSave}
          />
        ) : null}
      </Modal>
    </Stack>
  );
}

function describeError(err: unknown): string {
  const anyErr = err as {
    response?: { data?: { error?: string; details?: Record<string, string> } };
    message?: string;
  };
  const data = anyErr?.response?.data;
  if (data?.error) {
    if (data.details) {
      const parts = Object.entries(data.details).map(
        ([code, msg]) => `${code}: ${msg}`,
      );
      return `${data.error} (${parts.join("; ")})`;
    }
    return data.error;
  }
  return anyErr?.message ?? "Unknown error";
}

function showNotification(
  context: InvenTreePluginContext,
  message: string,
  color: string,
) {
  try {
    // The notifications module is provided by the host at runtime.
    const notifications = (window as any).MantineNotifications;
    notifications?.notifications?.show({ message, color });
  } catch {
    // Notifications are best-effort; ignore failures.
  }
}

function EditIcon() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
    </svg>
  );
}

function DeleteIcon() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M3 6h18" />
      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
    </svg>
  );
}

/**
 * Entry point called by InvenTree to render the panel.
 */
export function renderPanel(context: InvenTreePluginContext) {
  checkPluginVersion(context);
  return <LayoutsPanel context={context} />;
}
