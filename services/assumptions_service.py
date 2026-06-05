from schemas.assumptions import AssumptionsRequest, AssumptionsResponse, AssumptionItem

def extract_engineering_assumptions(request: AssumptionsRequest) -> AssumptionsResponse:
    """
    Phase 20.0: Engineering Assumptions Registry Engine
    Extracts, classifies, and documents all assumptions impacting quantity/cost estimation.
    """
    assumptions = []
    
    # 1. Analyze Known Constants (e.g., standard conversion rates, densities)
    for key, val in request.known_constants.items():
        name = str(key).lower()
        if "waste" in name or "wastage" in name:
            assumptions.append(AssumptionItem(
                name=key,
                value=float(val),
                unit="%",
                source="STANDARD_PRACTICE",
                reason="Standard industry material wastage allowance to cover breakages and cutting.",
                confidence="HIGH",
                override_allowed=True
            ))
        elif "density" in name or "weight" in name:
            assumptions.append(AssumptionItem(
                name=key,
                value=float(val),
                unit="kg/m3",
                source="ENGINEERING_JUDGMENT",
                reason="Standard bulk density utilized for converting geometric volume into mass.",
                confidence="HIGH",
                override_allowed=False
            ))
        else:
            assumptions.append(AssumptionItem(
                name=key,
                value=float(val),
                unit="unit",
                source="SYSTEM_DEFAULT",
                reason="System default conversion or property factor applied during takeoff.",
                confidence="MEDIUM",
                override_allowed=True
            ))

    # 2. Analyze Calculation Defaults (e.g., inferred geometry, baseline rates)
    for key, val in request.calculation_defaults.items():
        name = str(key).lower()
        if "height" in name or "thickness" in name or "depth" in name:
            assumptions.append(AssumptionItem(
                name=key,
                value=float(val),
                unit="m",
                source="ENGINEERING_JUDGMENT",
                reason="Fallback geometric value applied where architectural annotations were missing or illegible.",
                confidence="LOW",
                override_allowed=True
            ))
        elif "rate" in name or "price" in name or "cost" in name or "ugx" in name:
            assumptions.append(AssumptionItem(
                name=key,
                value=float(val),
                unit="UGX",
                source="LOCAL_MARKET",
                reason="Current estimated baseline market rate used in lieu of primary supplier quotations.",
                confidence="MEDIUM",
                override_allowed=True
            ))
        else:
            assumptions.append(AssumptionItem(
                name=key,
                value=float(val),
                unit="variable",
                source="SYSTEM_DEFAULT",
                reason="Algorithmic fill value used to sustain pipeline execution.",
                confidence="LOW",
                override_allowed=True
            ))

    # 3. Scan Material/Cost results for structurally embedded assumptions
    material_str = str(request.material_results).lower()
    if "blocks" in material_str or "blockwork" in material_str:
        assumptions.append(AssumptionItem(
            name="Blocks Solid Volume Factor",
            value=12.5,
            unit="blocks/m3",
            source="STANDARD_PRACTICE",
            reason="Based on 400x200x200mm standard masonry units plus 10mm mortar joint.",
            confidence="HIGH",
            override_allowed=True
        ))
    if "bricks" in material_str or "brickwork" in material_str:
        assumptions.append(AssumptionItem(
            name="Bricks Area Factor (Single Skin)",
            value=60.0,
            unit="bricks/m2",
            source="STANDARD_PRACTICE",
            reason="Based on 230x115x75mm standard clay bricks, half-brick wall with 10mm mortar bedding.",
            confidence="HIGH",
            override_allowed=True
        ))
    if "mortar" in material_str:
        assumptions.append(AssumptionItem(
            name="Mortar per 1000 Bricks",
            value=0.23,
            unit="m3",
            source="STANDARD_PRACTICE",
            reason="Standard wet mortar volume required per 1000 standard bricks including wastage.",
            confidence="HIGH",
            override_allowed=True
        ))

    summary = (
        f"Basis of Estimate Registry Complete. "
        f"Successfully identified and documented {len(assumptions)} explicit engineering assumptions underpinning the current BOQ. "
        "Professional validation is strongly advised for any parameter marked with a LOW confidence score or derived from fallback ENGINEERING_JUDGMENT."
    )

    return AssumptionsResponse(
        assumptions=assumptions,
        engineering_summary=summary
    )
