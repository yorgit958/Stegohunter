import os

directories = [
    "frontend/src/pages",
    "frontend/src/components",
    "frontend/src/layouts",
    "frontend/src/hooks",
    "frontend/src/store",
    "frontend/src/utils",
    "frontend/src/services",
]

pages = [
    "LoginPage.tsx",
    "RegisterPage.tsx",
    "DashboardPage.tsx",
    "ScanPage.tsx",
    "ScanResultPage.tsx",
    "NeutralizePage.tsx",
    "NeutralizeResultPage.tsx",
    "DNNAnalysisPage.tsx",
    "ReportsPage.tsx",
    "ReportDetailPage.tsx",
    "AdminPage.tsx",
    "NotFoundPage.tsx"
]

components = [
    "ScanUploader.tsx",
    "ScanProgress.tsx",
    "ThreatMap.tsx",
    "ComparisonSlider.tsx",
    "IntegrityReport.tsx",
    "WeightHeatmap.tsx",
    "YaraRuleEditor.tsx"
]

def scaffold():
    base_dir = r"c:\stego-hunter"
    os.chdir(base_dir)

    for d in directories:
        os.makedirs(d, exist_ok=True)
        print(f"Created: {d}")

    for p in pages:
        path = os.path.join("frontend/src/pages", p)
        if not os.path.exists(path):
            name = p.replace(".tsx", "")
            with open(path, "w") as f:
                f.write(f"import React from 'react';\n\nconst {name} = () => {{\n  return (\n    <div>\n      <h1>{name}</h1>\n    </div>\n  );\n}};\n\nexport default {name};\n")
            print(f"Created page: {path}")

    for c in components:
        path = os.path.join("frontend/src/components", c)
        if not os.path.exists(path):
             name = c.replace(".tsx", "")
             with open(path, "w") as f:
                  f.write(f"import React from 'react';\n\nconst {name} = () => {{\n  return (\n    <div>\n      <h2>{name} Component</h2>\n    </div>\n  );\n}};\n\nexport default {name};\n")
             print(f"Created component: {path}")

if __name__ == "__main__":
    scaffold()
