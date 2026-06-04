"""
Tool 83 - Formula Sheet Manager
Store Physics/Chemistry/Math formulas with descriptions and units.
Search by keyword, browse by topic, display beautifully.
Export all formulas as a plain-text study sheet.
Run: python 83_formula_sheet.py
"""

import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.columns import Columns
from rich import box

console = Console()

DATA_FILE = Path(__file__).parent / "formulas.json"

# ── built-in formula database ─────────────────────────────────────────────────

BUILTIN_FORMULAS = {
    "Physics": {
        "Mechanics": [
            {"name": "Newton's Second Law",       "formula": "F = ma",                    "description": "Force equals mass times acceleration", "units": "N = kg·m/s²"},
            {"name": "Work Done",                  "formula": "W = F·d·cosθ",              "description": "Work done by force F over displacement d at angle θ", "units": "J (Joule)"},
            {"name": "Kinetic Energy",             "formula": "KE = ½mv²",                 "description": "Energy of a body due to its motion", "units": "J"},
            {"name": "Potential Energy",           "formula": "PE = mgh",                  "description": "Gravitational potential energy near Earth's surface", "units": "J"},
            {"name": "Equations of Motion (v)",    "formula": "v = u + at",                "description": "Final velocity from initial velocity u, acceleration a, time t", "units": "m/s"},
            {"name": "Equations of Motion (s)",    "formula": "s = ut + ½at²",             "description": "Displacement from initial velocity, acceleration and time", "units": "m"},
            {"name": "Equations of Motion (v²)",   "formula": "v² = u² + 2as",             "description": "Velocity-displacement relation without time", "units": "m²/s²"},
            {"name": "Momentum",                   "formula": "p = mv",                    "description": "Product of mass and velocity", "units": "kg·m/s"},
            {"name": "Impulse",                    "formula": "J = FΔt = Δp",              "description": "Change in momentum equals impulse", "units": "N·s"},
            {"name": "Centripetal Acceleration",   "formula": "a_c = v²/r = ω²r",          "description": "Acceleration directed toward center of circular path", "units": "m/s²"},
            {"name": "Torque",                     "formula": "τ = r × F = Iα",            "description": "Rotational equivalent of force", "units": "N·m"},
            {"name": "Moment of Inertia",          "formula": "I = Σmr²",                  "description": "Rotational inertia; for solid sphere: I = 2/5 mr²", "units": "kg·m²"},
            {"name": "Projectile Range",           "formula": "R = u²sin(2θ)/g",           "description": "Horizontal range of a projectile launched at angle θ", "units": "m"},
            {"name": "Escape Velocity",            "formula": "v_e = √(2GM/R)",            "description": "Minimum speed to escape a planet's gravity", "units": "m/s"},
            {"name": "Gravitational Force",        "formula": "F = Gm₁m₂/r²",             "description": "Newton's law of universal gravitation", "units": "N"},
        ],
        "Waves & Oscillations": [
            {"name": "Simple Harmonic Motion",     "formula": "x = A·sin(ωt + φ)",         "description": "Displacement in SHM; A=amplitude, ω=angular freq", "units": "m"},
            {"name": "Time Period (SHM)",           "formula": "T = 2π/ω = 2π√(m/k)",      "description": "Period of oscillation", "units": "s"},
            {"name": "Wave Speed",                 "formula": "v = fλ",                    "description": "Wave speed = frequency × wavelength", "units": "m/s"},
            {"name": "Speed of Sound",             "formula": "v = √(γP/ρ) = √(γRT/M)",   "description": "Speed of sound in gas; γ=adiabatic index", "units": "m/s"},
            {"name": "Doppler Effect",             "formula": "f' = f(v±v_o)/(v∓v_s)",    "description": "Observed frequency when source/observer moves", "units": "Hz"},
        ],
        "Electrostatics": [
            {"name": "Coulomb's Law",              "formula": "F = kq₁q₂/r²",             "description": "Electrostatic force between two charges; k=9×10⁹ N·m²/C²", "units": "N"},
            {"name": "Electric Field",             "formula": "E = F/q = kQ/r²",           "description": "Force per unit positive charge", "units": "N/C = V/m"},
            {"name": "Electric Potential",         "formula": "V = kQ/r",                  "description": "Work done to bring unit charge from infinity", "units": "V (Volt)"},
            {"name": "Capacitance",                "formula": "C = Q/V = ε₀A/d",          "description": "Ability to store charge; parallel plate formula", "units": "F (Farad)"},
            {"name": "Energy in Capacitor",        "formula": "U = ½CV² = Q²/2C",         "description": "Energy stored in a charged capacitor", "units": "J"},
            {"name": "Ohm's Law",                  "formula": "V = IR",                    "description": "Voltage equals current times resistance", "units": "V, A, Ω"},
            {"name": "Power (Electrical)",         "formula": "P = VI = I²R = V²/R",      "description": "Electrical power dissipated", "units": "W (Watt)"},
        ],
        "Optics": [
            {"name": "Snell's Law",                "formula": "n₁sinθ₁ = n₂sinθ₂",        "description": "Refraction of light at an interface", "units": "dimensionless"},
            {"name": "Lens Formula",               "formula": "1/f = 1/v - 1/u",           "description": "Relation between focal length, image and object distance", "units": "m (or cm)"},
            {"name": "Mirror Formula",             "formula": "1/f = 1/v + 1/u",           "description": "Relation for spherical mirrors (sign convention)", "units": "m"},
            {"name": "Magnification",              "formula": "m = -v/u = h_i/h_o",        "description": "Ratio of image size to object size", "units": "dimensionless"},
            {"name": "Critical Angle",             "formula": "sinC = n₂/n₁ = 1/n",       "description": "Angle beyond which total internal reflection occurs", "units": "degrees"},
        ],
        "Modern Physics": [
            {"name": "Photoelectric Effect",       "formula": "E = hν = φ + ½mv²_max",    "description": "Energy of photon; φ = work function", "units": "J or eV"},
            {"name": "de Broglie Wavelength",      "formula": "λ = h/mv = h/p",           "description": "Wave nature of matter; h = 6.626×10⁻³⁴ J·s", "units": "m"},
            {"name": "Einstein Mass-Energy",       "formula": "E = mc²",                   "description": "Mass-energy equivalence; c = 3×10⁸ m/s", "units": "J"},
            {"name": "Radioactive Decay",          "formula": "N = N₀e^(-λt)",             "description": "Number of undecayed nuclei at time t", "units": "atoms"},
            {"name": "Half-Life",                  "formula": "t½ = ln2/λ = 0.693/λ",     "description": "Time for half the nuclei to decay", "units": "s"},
        ],
        "Thermodynamics": [
            {"name": "First Law of Thermo",        "formula": "ΔU = Q - W",               "description": "Change in internal energy = heat added - work done", "units": "J"},
            {"name": "Ideal Gas Law",              "formula": "PV = nRT",                  "description": "P=pressure, V=volume, n=moles, R=8.314 J/mol·K", "units": "Pa·m³"},
            {"name": "Carnot Efficiency",          "formula": "η = 1 - T_C/T_H",          "description": "Maximum efficiency of a heat engine", "units": "%"},
            {"name": "Entropy Change",             "formula": "ΔS = Q_rev/T",             "description": "Change in entropy for reversible process", "units": "J/K"},
        ],
    },
    "Chemistry": {
        "Physical Chemistry": [
            {"name": "Ideal Gas Law",              "formula": "PV = nRT",                  "description": "R = 8.314 J/mol·K = 0.0821 L·atm/mol·K", "units": "atm·L or J"},
            {"name": "Gibbs Free Energy",          "formula": "ΔG = ΔH - TΔS",           "description": "Spontaneity: ΔG<0 spontaneous, ΔG>0 non-spontaneous", "units": "kJ/mol"},
            {"name": "Equilibrium Constant",       "formula": "K = [products]^p/[reactants]^r", "description": "Ratio of product to reactant concentrations at equilibrium", "units": "varies"},
            {"name": "Henderson-Hasselbalch",      "formula": "pH = pKa + log([A⁻]/[HA])", "description": "pH of a buffer solution", "units": "dimensionless"},
            {"name": "Raoult's Law",               "formula": "P_A = x_A · P°_A",         "description": "Partial vapour pressure of component in ideal solution", "units": "atm"},
            {"name": "Rate Law",                   "formula": "r = k[A]^m[B]^n",          "description": "Rate of reaction; k=rate constant, m,n=orders", "units": "mol/L·s"},
            {"name": "Arrhenius Equation",         "formula": "k = Ae^(-Ea/RT)",           "description": "Temperature dependence of rate constant; Ea=activation energy", "units": "s⁻¹"},
            {"name": "Nernst Equation",            "formula": "E = E° - (RT/nF)lnQ",      "description": "Cell potential at non-standard conditions", "units": "V"},
            {"name": "Faraday's Law (electrolysis)","formula": "m = MIt/nF",              "description": "Mass deposited in electrolysis; F=96485 C/mol", "units": "g"},
            {"name": "Osmotic Pressure",           "formula": "π = MRT",                  "description": "Osmotic pressure of a solution; M=molarity", "units": "atm"},
            {"name": "Boiling Point Elevation",    "formula": "ΔTb = Kb·m",              "description": "Elevation of boiling point by solute; Kb=ebullioscopic constant", "units": "°C"},
            {"name": "Freezing Point Depression",  "formula": "ΔTf = Kf·m",              "description": "Depression of freezing point; Kf=cryoscopic constant", "units": "°C"},
        ],
        "Organic Chemistry": [
            {"name": "Degree of Unsaturation",     "formula": "DoU = (2C + 2 + N - H - X)/2", "description": "Rings + double bonds in an organic molecule", "units": "dimensionless"},
            {"name": "Empirical Formula",          "formula": "Molar mass / Empirical formula mass = n", "description": "n gives molecular formula from empirical formula", "units": "dimensionless"},
        ],
        "Atomic Structure": [
            {"name": "Rydberg Formula",            "formula": "1/λ = R_H(1/n₁² - 1/n₂²)", "description": "Wavelengths of spectral lines; R_H = 1.097×10⁷ m⁻¹", "units": "m⁻¹"},
            {"name": "Energy of Hydrogen Orbital", "formula": "E_n = -13.6/n² eV",        "description": "Energy of electron in nth orbit of hydrogen", "units": "eV"},
            {"name": "de Broglie (Bohr orbit)",    "formula": "nλ = 2πr",                 "description": "Standing wave condition for electron orbits", "units": "m"},
        ],
    },
    "Mathematics": {
        "Algebra": [
            {"name": "Quadratic Formula",          "formula": "x = (-b ± √(b²-4ac)) / 2a", "description": "Roots of ax² + bx + c = 0", "units": "dimensionless"},
            {"name": "Sum of AP",                  "formula": "S_n = n/2 · (2a + (n-1)d)", "description": "Sum of arithmetic progression; a=first term, d=common diff", "units": "dimensionless"},
            {"name": "nth term of AP",             "formula": "a_n = a + (n-1)d",          "description": "nth term of arithmetic progression", "units": "dimensionless"},
            {"name": "Sum of GP",                  "formula": "S_n = a(rⁿ-1)/(r-1)",      "description": "Sum of geometric progression; r=common ratio, r≠1", "units": "dimensionless"},
            {"name": "Sum of Infinite GP",         "formula": "S∞ = a/(1-r),  |r|<1",     "description": "Sum of infinite converging GP", "units": "dimensionless"},
            {"name": "Binomial Theorem",           "formula": "(a+b)ⁿ = Σ C(n,r)aⁿ⁻ʳbʳ", "description": "Expansion of (a+b)^n; C(n,r)=n!/(r!(n-r)!)", "units": "dimensionless"},
            {"name": "Permutation",                "formula": "P(n,r) = n!/(n-r)!",        "description": "Ordered arrangements of r items from n", "units": "dimensionless"},
            {"name": "Combination",                "formula": "C(n,r) = n!/(r!(n-r)!)",   "description": "Unordered selections of r items from n", "units": "dimensionless"},
        ],
        "Trigonometry": [
            {"name": "Pythagorean Identity",       "formula": "sin²θ + cos²θ = 1",        "description": "Fundamental trig identity", "units": "dimensionless"},
            {"name": "Sine Rule",                  "formula": "a/sinA = b/sinB = c/sinC", "description": "Relation in any triangle", "units": "dimensionless"},
            {"name": "Cosine Rule",                "formula": "c² = a² + b² - 2ab·cosC",  "description": "Generalisation of Pythagorean theorem", "units": "length²"},
            {"name": "Double Angle (sin)",         "formula": "sin2θ = 2sinθcosθ",         "description": "Double angle formula for sine", "units": "dimensionless"},
            {"name": "Double Angle (cos)",         "formula": "cos2θ = cos²θ - sin²θ",    "description": "Double angle formula for cosine", "units": "dimensionless"},
            {"name": "Product to Sum (sinA·cosB)","formula": "sinAcosB = ½[sin(A+B)+sin(A-B)]", "description": "Product-to-sum conversion", "units": "dimensionless"},
        ],
        "Calculus": [
            {"name": "Power Rule (derivative)",    "formula": "d/dx(xⁿ) = nxⁿ⁻¹",        "description": "Derivative of power function", "units": "dimensionless"},
            {"name": "Chain Rule",                 "formula": "dy/dx = (dy/du)·(du/dx)",  "description": "Derivative of composite functions", "units": "dimensionless"},
            {"name": "Product Rule",               "formula": "d(uv)/dx = u'v + uv'",     "description": "Derivative of product of two functions", "units": "dimensionless"},
            {"name": "Quotient Rule",              "formula": "d(u/v)/dx = (u'v - uv')/v²","description": "Derivative of quotient of two functions", "units": "dimensionless"},
            {"name": "Fundamental Theorem",        "formula": "∫_a^b f(x)dx = F(b)-F(a)", "description": "Definite integral = antiderivative evaluated at limits", "units": "dimensionless"},
            {"name": "Limit Definition",           "formula": "f'(x) = lim(h→0) [f(x+h)-f(x)]/h", "description": "First principles definition of derivative", "units": "dimensionless"},
            {"name": "Integration by Parts",       "formula": "∫u dv = uv - ∫v du",      "description": "Integration technique for products", "units": "dimensionless"},
        ],
        "Coordinate Geometry": [
            {"name": "Distance Formula",           "formula": "d = √((x₂-x₁)²+(y₂-y₁)²)", "description": "Distance between two points", "units": "length"},
            {"name": "Section Formula",            "formula": "P = ((mx₂+nx₁)/(m+n), (my₂+ny₁)/(m+n))", "description": "Point dividing segment in ratio m:n", "units": "length"},
            {"name": "Slope of Line",              "formula": "m = tanθ = (y₂-y₁)/(x₂-x₁)","description": "Gradient of a line", "units": "dimensionless"},
            {"name": "Circle Equation",            "formula": "x² + y² + 2gx + 2fy + c = 0","description": "General form of circle; centre=(-g,-f), radius=√(g²+f²-c)", "units": "length"},
            {"name": "Area of Triangle",           "formula": "A = ½|x₁(y₂-y₃)+x₂(y₃-y₁)+x₃(y₁-y₂)|","description": "Area using coordinate geometry", "units": "length²"},
        ],
        "Probability & Statistics": [
            {"name": "Probability",                "formula": "P(A) = n(A)/n(S)",          "description": "Probability of event A; n=number of outcomes", "units": "dimensionless [0,1]"},
            {"name": "Bayes' Theorem",             "formula": "P(A|B) = P(B|A)P(A)/P(B)", "description": "Conditional probability reversal", "units": "dimensionless"},
            {"name": "Mean (Statistics)",          "formula": "x̄ = Σx_i / n",            "description": "Arithmetic mean of data set", "units": "same as data"},
            {"name": "Standard Deviation",         "formula": "σ = √(Σ(xᵢ-x̄)²/n)",      "description": "Measure of spread of data", "units": "same as data"},
            {"name": "Binomial Distribution",      "formula": "P(X=k) = C(n,k)pᵏ(1-p)ⁿ⁻ᵏ","description": "Probability of k successes in n trials", "units": "dimensionless"},
        ],
    },
}

# ── helpers ───────────────────────────────────────────────────────────────────

def load_formulas() -> dict:
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return BUILTIN_FORMULAS

def save_formulas(formulas: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(formulas, f, indent=2, ensure_ascii=False)
    console.print(f"[green]✅ Saved to {DATA_FILE.name}[/green]")

def _flat_list(formulas: dict) -> list:
    """Flatten nested structure into a list of dicts with subject/topic keys."""
    flat = []
    for subject, topics in formulas.items():
        for topic, flist in topics.items():
            for f in flist:
                flat.append({**f, "_subject": subject, "_topic": topic})
    return flat

def display_formula_panel(f: dict):
    content = (
        f"[bold yellow]{f['formula']}[/bold yellow]\n\n"
        f"[dim]{f['description']}[/dim]\n"
        f"[cyan]Units:[/cyan] {f['units']}"
    )
    console.print(Panel(content, title=f"[bold]{f['name']}[/bold]  [{f['_subject']} / {f['_topic']}]", border_style="cyan"))

# ── menu functions ────────────────────────────────────────────────────────────

def browse_by_topic(formulas: dict):
    console.print("\n[bold cyan]📖 BROWSE BY TOPIC[/bold cyan]")
    subjects = list(formulas.keys())
    for i, s in enumerate(subjects, 1):
        console.print(f"  [cyan]{i}[/cyan] - {s}")
    s_choice = Prompt.ask("Select subject", default="1")
    try:
        subject = subjects[int(s_choice) - 1]
    except (ValueError, IndexError):
        console.print("[red]Invalid.[/red]")
        return

    topics = list(formulas[subject].keys())
    console.print(f"\n[bold]Topics in {subject}:[/bold]")
    for i, t in enumerate(topics, 1):
        console.print(f"  [cyan]{i}[/cyan] - {t}")
    t_choice = Prompt.ask("Select topic", default="1")
    try:
        topic = topics[int(t_choice) - 1]
    except (ValueError, IndexError):
        console.print("[red]Invalid.[/red]")
        return

    flist = formulas[subject][topic]
    console.print(f"\n[bold green]{len(flist)} formulas in {subject} / {topic}:[/bold green]\n")
    for f in flist:
        display_formula_panel({**f, "_subject": subject, "_topic": topic})

def search_formulas(formulas: dict):
    console.print("\n[bold cyan]🔍 SEARCH FORMULAS[/bold cyan]")
    query = Prompt.ask("Search keyword").lower()
    flat = _flat_list(formulas)
    results = [f for f in flat if
               query in f["name"].lower() or
               query in f["formula"].lower() or
               query in f["description"].lower() or
               query in f["_topic"].lower() or
               query in f["_subject"].lower()]
    if not results:
        console.print(f"[red]No formulas found for '{query}'[/red]")
        return
    console.print(f"\n[green]{len(results)} result(s) for '[bold]{query}[/bold]':[/green]\n")
    for f in results:
        display_formula_panel(f)

def add_formula(formulas: dict):
    console.print("\n[bold cyan]➕ ADD FORMULA[/bold cyan]")
    subjects = list(formulas.keys())
    for i, s in enumerate(subjects, 1):
        console.print(f"  [cyan]{i}[/cyan] - {s}")
    console.print(f"  [cyan]{len(subjects)+1}[/cyan] - New subject")
    s_choice = Prompt.ask("Select subject")
    try:
        idx = int(s_choice) - 1
        if idx < len(subjects):
            subject = subjects[idx]
        else:
            subject = Prompt.ask("New subject name")
            formulas[subject] = {}
    except ValueError:
        subject = s_choice
        formulas.setdefault(subject, {})

    topics = list(formulas.get(subject, {}).keys())
    for i, t in enumerate(topics, 1):
        console.print(f"  [cyan]{i}[/cyan] - {t}")
    console.print(f"  [cyan]{len(topics)+1}[/cyan] - New topic")
    t_choice = Prompt.ask("Select topic")
    try:
        idx = int(t_choice) - 1
        if idx < len(topics):
            topic = topics[idx]
        else:
            topic = Prompt.ask("New topic name")
            formulas[subject][topic] = []
    except ValueError:
        topic = t_choice
        formulas[subject].setdefault(topic, [])

    name = Prompt.ask("Formula name")
    formula = Prompt.ask("Formula (use Unicode: ², ³, α, β, γ, Δ, λ, θ)")
    description = Prompt.ask("Description")
    units = Prompt.ask("Units")
    formulas[subject][topic].append({"name": name, "formula": formula, "description": description, "units": units})
    save_formulas(formulas)
    console.print(f"[green]✅ Formula '{name}' added to {subject}/{topic}.[/green]")

def export_text(formulas: dict):
    out_path = Path(__file__).parent / "formula_sheet_export.txt"
    lines = ["=" * 70, "  FORMULA SHEET — PHYSICS / CHEMISTRY / MATHEMATICS", "=" * 70, ""]
    for subject, topics in formulas.items():
        lines.append(f"\n{'═' * 60}")
        lines.append(f"  {subject.upper()}")
        lines.append(f"{'═' * 60}")
        for topic, flist in topics.items():
            lines.append(f"\n  ── {topic} ──")
            for f in flist:
                lines.append(f"  • {f['name']}")
                lines.append(f"      Formula: {f['formula']}")
                lines.append(f"      Info:    {f['description']}")
                lines.append(f"      Units:   {f['units']}")
    with open(out_path, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))
    console.print(f"[green]✅ Exported to {out_path}[/green]")

def show_summary(formulas: dict):
    table = Table(title="📊 Formula Sheet Summary", box=box.ROUNDED, header_style="bold magenta")
    table.add_column("Subject", style="cyan")
    table.add_column("Topics", justify="center")
    table.add_column("Formulas", justify="center", style="bold green")
    total = 0
    for subject, topics in formulas.items():
        count = sum(len(v) for v in topics.values())
        total += count
        table.add_row(subject, str(len(topics)), str(count))
    table.add_row("[bold]TOTAL[/bold]", "—", f"[bold]{total}[/bold]")
    console.print(table)

# ── main ──────────────────────────────────────────────────────────────────────

def main():
    console.print(Panel.fit(
        "[bold cyan]📐 FORMULA SHEET MANAGER[/bold cyan]\n"
        "[dim]Physics · Chemistry · Mathematics — NEET/JEE Ready[/dim]",
        border_style="cyan"
    ))
    formulas = load_formulas()

    menu = {
        "1": ("Browse by Topic", browse_by_topic),
        "2": ("Search Formulas", search_formulas),
        "3": ("Add Custom Formula", add_formula),
        "4": ("Summary / Stats", show_summary),
        "5": ("Export to Text File", export_text),
        "6": ("Save Changes", lambda f: save_formulas(f)),
        "7": ("Exit", None),
    }

    while True:
        console.print("\n[bold]MENU:[/bold]")
        for k, (label, _) in menu.items():
            console.print(f"  [cyan]{k}[/cyan] - {label}")
        choice = Prompt.ask("Choose", choices=list(menu.keys()))
        if choice == "7":
            console.print("[dim]Formula sheet saved. Study hard! 📚[/dim]")
            break
        _, fn = menu[choice]
        fn(formulas)

if __name__ == "__main__":
    main()
