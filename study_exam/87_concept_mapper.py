"""
Tool 87 - Concept Map Builder
Build hierarchical concept maps with nodes and relationships.
Add concepts, link them with labeled relationships, navigate the map,
and export as an ASCII text tree. Perfect for Biology/Chemistry topics.
Run: python 87_concept_mapper.py
"""

import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.tree import Tree
from rich import box

console = Console()

DATA_FILE = Path(__file__).parent / "concept_maps.json"

# ── built-in sample maps ──────────────────────────────────────────────────────

SAMPLE_MAPS = {
    "Cell Biology": {
        "nodes": {
            "Cell": {
                "description": "Fundamental unit of life",
                "children": [
                    {"child": "Prokaryotic Cell", "relation": "includes"},
                    {"child": "Eukaryotic Cell",  "relation": "includes"},
                ]
            },
            "Prokaryotic Cell": {
                "description": "No membrane-bound nucleus; bacteria, archaea",
                "children": [
                    {"child": "Nucleoid",          "relation": "has"},
                    {"child": "Cell Wall",         "relation": "has"},
                    {"child": "Plasmid",           "relation": "may have"},
                ]
            },
            "Eukaryotic Cell": {
                "description": "Has membrane-bound nucleus and organelles",
                "children": [
                    {"child": "Nucleus",           "relation": "contains"},
                    {"child": "Mitochondria",      "relation": "contains"},
                    {"child": "Endoplasmic Reticulum", "relation": "contains"},
                    {"child": "Golgi Apparatus",   "relation": "contains"},
                    {"child": "Ribosome",          "relation": "contains"},
                    {"child": "Lysosome",          "relation": "contains"},
                ]
            },
            "Nucleus": {
                "description": "Control centre; contains DNA",
                "children": [
                    {"child": "Chromatin",         "relation": "contains"},
                    {"child": "Nucleolus",         "relation": "contains"},
                    {"child": "Nuclear Envelope",  "relation": "bounded by"},
                ]
            },
            "Mitochondria": {
                "description": "Powerhouse; site of cellular respiration",
                "children": [
                    {"child": "Inner Membrane",    "relation": "has"},
                    {"child": "Cristae",           "relation": "has"},
                    {"child": "Matrix",            "relation": "has"},
                    {"child": "ATP Production",    "relation": "produces"},
                ]
            },
            "Endoplasmic Reticulum": {
                "description": "Network for protein and lipid synthesis",
                "children": [
                    {"child": "Rough ER",          "relation": "includes"},
                    {"child": "Smooth ER",         "relation": "includes"},
                ]
            },
            "Rough ER":      {"description": "Has ribosomes; protein synthesis", "children": []},
            "Smooth ER":     {"description": "No ribosomes; lipid synthesis, detox", "children": []},
            "Golgi Apparatus": {"description": "Post office of the cell; processes and ships proteins", "children": []},
            "Ribosome":      {"description": "Site of protein synthesis; 70S (prokaryotes), 80S (eukaryotes)", "children": []},
            "Lysosome":      {"description": "Suicide bags; digestive enzymes", "children": []},
            "Nucleoid":      {"description": "Region with DNA in prokaryotes (no membrane)", "children": []},
            "Cell Wall":     {"description": "Peptidoglycan in bacteria; rigid support", "children": []},
            "Plasmid":       {"description": "Small circular extra-chromosomal DNA", "children": []},
            "Chromatin":     {"description": "DNA + histone proteins; condenses to chromosomes", "children": []},
            "Nucleolus":     {"description": "Site of rRNA synthesis and ribosome assembly", "children": []},
            "Nuclear Envelope": {"description": "Double membrane; nuclear pores for transport", "children": []},
            "Inner Membrane": {"description": "Folded into cristae; site of electron transport chain", "children": []},
            "Cristae":       {"description": "Infoldings of inner mitochondrial membrane; ETC and ATP synthase", "children": []},
            "Matrix":        {"description": "Site of Krebs cycle; contains mitochondrial DNA", "children": []},
            "ATP Production": {"description": "36-38 ATP per glucose via oxidative phosphorylation", "children": []},
        },
        "root": "Cell",
    },
    "Photosynthesis": {
        "nodes": {
            "Photosynthesis": {
                "description": "Process of converting light energy to chemical energy",
                "children": [
                    {"child": "Light Reactions", "relation": "phase 1"},
                    {"child": "Calvin Cycle",    "relation": "phase 2"},
                ]
            },
            "Light Reactions": {
                "description": "Occur in thylakoid membranes; capture light energy",
                "children": [
                    {"child": "Photosystem II", "relation": "involves"},
                    {"child": "Photosystem I",  "relation": "involves"},
                    {"child": "ATP & NADPH",    "relation": "produces"},
                    {"child": "Oxygen",         "relation": "releases"},
                ]
            },
            "Calvin Cycle": {
                "description": "Occurs in stroma; uses ATP & NADPH to fix CO₂",
                "children": [
                    {"child": "Carbon Fixation",         "relation": "step 1"},
                    {"child": "Reduction",               "relation": "step 2"},
                    {"child": "Regeneration of RuBP",    "relation": "step 3"},
                    {"child": "G3P (Glucose precursor)", "relation": "produces"},
                ]
            },
            "Photosystem II":  {"description": "P680; splits water (photolysis); releases O₂", "children": []},
            "Photosystem I":   {"description": "P700; reduces NADP⁺ to NADPH", "children": []},
            "ATP & NADPH":     {"description": "Assimilatory power; used in Calvin cycle", "children": []},
            "Oxygen":          {"description": "By-product of water splitting in PS-II", "children": []},
            "Carbon Fixation": {"description": "CO₂ + RuBP → 2 × 3-PGA (by RuBisCO)", "children": []},
            "Reduction":       {"description": "3-PGA reduced to G3P using ATP and NADPH", "children": []},
            "Regeneration of RuBP": {"description": "G3P regenerates RuBP using ATP (5 carbon acceptor)", "children": []},
            "G3P (Glucose precursor)": {"description": "3-carbon compound; used to make glucose", "children": []},
        },
        "root": "Photosynthesis",
    },
}

# ── helpers ───────────────────────────────────────────────────────────────────

def load_maps() -> dict:
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return SAMPLE_MAPS.copy()

def save_maps(maps: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(maps, f, indent=2, ensure_ascii=False)
    console.print(f"[green]✅ Saved to {DATA_FILE.name}[/green]")

def _choose_map(maps: dict) -> str | None:
    names = list(maps.keys())
    for i, n in enumerate(names, 1):
        console.print(f"  [cyan]{i}[/cyan] - {n}")
    choice = Prompt.ask("Select map", default="1")
    try:
        return names[int(choice) - 1]
    except (ValueError, IndexError):
        return None

def _build_tree(nodes: dict, root: str, visited: set | None = None) -> Tree:
    if visited is None:
        visited = set()
    if root in visited:
        return Tree(f"[dim]{root} (circular ref)[/dim]")
    visited.add(root)
    node = nodes.get(root, {})
    desc = node.get("description", "")
    label = f"[bold cyan]{root}[/bold cyan]" + (f" [dim]— {desc}[/dim]" if desc else "")
    tree = Tree(label)
    for child_info in node.get("children", []):
        child = child_info.get("child", "")
        relation = child_info.get("relation", "→")
        subtree = _build_tree(nodes, child, visited.copy())
        branch_label = f"[yellow]─({relation})→[/yellow] " + subtree.label
        subtree.label = branch_label
        tree.children.append(subtree)
    return tree

def _tree_to_text(nodes: dict, root: str, prefix: str = "", visited: set | None = None) -> list:
    if visited is None:
        visited = set()
    if root in visited:
        return [prefix + f"[{root} — circular]"]
    visited.add(root)
    lines = [prefix + root]
    node = nodes.get(root, {})
    for child_info in node.get("children", []):
        child = child_info["child"]
        relation = child_info.get("relation", "→")
        lines.append(prefix + f"  └─({relation})→ {child}")
        lines.extend(_tree_to_text(nodes, child, prefix + "      ", visited.copy()))
    return lines

# ── menu functions ────────────────────────────────────────────────────────────

def view_map(maps: dict):
    console.print("\n[bold cyan]🗺️  VIEW CONCEPT MAP[/bold cyan]")
    if not maps:
        console.print("[yellow]No maps. Create one first.[/yellow]")
        return
    map_name = _choose_map(maps)
    if not map_name:
        return
    m = maps[map_name]
    root = m.get("root", list(m["nodes"].keys())[0])
    tree = _build_tree(m["nodes"], root)
    console.print(Panel(tree, title=f"[bold]{map_name}[/bold]", border_style="cyan"))

def create_map(maps: dict):
    console.print("\n[bold cyan]➕ CREATE CONCEPT MAP[/bold cyan]")
    name = Prompt.ask("Map name (e.g. 'Genetics')")
    if name in maps:
        console.print("[red]Map already exists.[/red]")
        return
    root = Prompt.ask("Root concept (e.g. 'DNA')")
    desc = Prompt.ask("Root description")
    maps[name] = {"nodes": {root: {"description": desc, "children": []}}, "root": root}
    save_maps(maps)
    console.print(f"[green]✅ Map '{name}' created with root '{root}'.[/green]")

def add_node(maps: dict):
    console.print("\n[bold cyan]➕ ADD CONCEPT / NODE[/bold cyan]")
    if not maps:
        console.print("[yellow]No maps.[/yellow]")
        return
    map_name = _choose_map(maps)
    if not map_name:
        return
    m = maps[map_name]
    nodes = m["nodes"]
    console.print("[bold]Existing nodes:[/bold]")
    for name in nodes:
        console.print(f"  • {name}")
    parent = Prompt.ask("Parent concept (must exist above)")
    if parent not in nodes:
        console.print(f"[red]'{parent}' not found in map.[/red]")
        return
    child = Prompt.ask("New concept name")
    relation = Prompt.ask("Relationship label (e.g. 'contains', 'produces', 'is a')", default="is a")
    desc = Prompt.ask("Description for new concept")
    nodes.setdefault(parent, {"description": "", "children": []})["children"].append({"child": child, "relation": relation})
    nodes[child] = {"description": desc, "children": []}
    save_maps(maps)
    console.print(f"[green]✅ '{child}' added under '{parent}' with relation '{relation}'.[/green]")

def search_concept(maps: dict):
    console.print("\n[bold cyan]🔍 SEARCH CONCEPT[/bold cyan]")
    query = Prompt.ask("Concept name (partial OK)").lower()
    found = []
    for map_name, m in maps.items():
        for node_name, node in m["nodes"].items():
            if query in node_name.lower() or query in node.get("description", "").lower():
                found.append((map_name, node_name, node.get("description", "")))
    if not found:
        console.print(f"[red]No concepts matching '{query}'.[/red]")
        return
    table = Table(title=f"🔍 Results for '{query}'", box=box.ROUNDED, header_style="bold magenta")
    table.add_column("Map", style="cyan")
    table.add_column("Concept", style="bold yellow")
    table.add_column("Description")
    for map_name, concept, desc in found:
        table.add_row(map_name, concept, desc)
    console.print(table)

def export_map(maps: dict):
    console.print("\n[bold cyan]📤 EXPORT MAP AS TEXT TREE[/bold cyan]")
    if not maps:
        console.print("[yellow]No maps.[/yellow]")
        return
    map_name = _choose_map(maps)
    if not map_name:
        return
    m = maps[map_name]
    root = m.get("root", list(m["nodes"].keys())[0])
    lines = _tree_to_text(m["nodes"], root)
    out_path = Path(__file__).parent / f"concept_map_{map_name.replace(' ', '_')}.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"CONCEPT MAP: {map_name}\n")
        f.write("=" * 50 + "\n")
        f.write("\n".join(lines))
    console.print(f"[green]✅ Exported to {out_path}[/green]")
    for line in lines[:30]:
        console.print(f"[dim]{line}[/dim]")

def list_maps(maps: dict):
    if not maps:
        console.print("[yellow]No maps yet.[/yellow]")
        return
    table = Table(title="🗺️ Concept Maps", box=box.ROUNDED, header_style="bold magenta")
    table.add_column("Map", style="cyan")
    table.add_column("Root", style="yellow")
    table.add_column("Nodes", justify="center", style="green")
    for name, m in maps.items():
        root = m.get("root", "?")
        table.add_row(name, root, str(len(m["nodes"])))
    console.print(table)

def main():
    console.print(Panel.fit(
        "[bold cyan]🗺️  CONCEPT MAP BUILDER[/bold cyan]\n"
        "[dim]Build · Navigate · Explore hierarchical concept maps[/dim]",
        border_style="cyan"
    ))
    maps = load_maps()

    menu = {
        "1": ("View Concept Map", view_map),
        "2": ("Create New Map", create_map),
        "3": ("Add Concept / Node", add_node),
        "4": ("Search Concept", search_concept),
        "5": ("List All Maps", list_maps),
        "6": ("Export Map as Text", export_map),
        "7": ("Exit", None),
    }

    while True:
        console.print("\n[bold]MENU:[/bold]")
        for k, (label, _) in menu.items():
            console.print(f"  [cyan]{k}[/cyan] - {label}")
        choice = Prompt.ask("Choose", choices=list(menu.keys()))
        if choice == "7":
            console.print("[dim]Keep mapping your knowledge! 🗺️[/dim]")
            break
        _, fn = menu[choice]
        fn(maps)

if __name__ == "__main__":
    main()
