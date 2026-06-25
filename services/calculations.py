def calculate_actual_kpis(arrivals, contracts, closing_rate, avg_price):
    qs = contracts / (closing_rate / 100) if closing_rate else 0
    penetration = (qs / arrivals * 100) if arrivals else 0
    volume = contracts * avg_price
    vpg = volume / qs if qs else 0

    return {
        "Qs": qs,
        "Penetration": penetration,
        "Volume": volume,
        "VPG": vpg,
    }


def calculate_projection(arrivals, contracts, qs, volume, days_elapsed, days_in_month):
    def project_mtd(value):
        return (value / days_elapsed) * days_in_month if days_elapsed else 0

    proj_arrivals = project_mtd(arrivals)
    proj_contracts = project_mtd(contracts)
    proj_qs = project_mtd(qs)
    proj_volume = project_mtd(volume)

    proj_penetration = (proj_qs / proj_arrivals * 100) if proj_arrivals else 0
    proj_closing_rate = (proj_contracts / proj_qs * 100) if proj_qs else 0
    proj_vpg = (proj_volume / proj_qs) if proj_qs else 0
    proj_avg_price = (proj_volume / proj_contracts) if proj_contracts else 0

    return {
        "Arrivals": proj_arrivals,
        "Contracts": proj_contracts,
        "Qs": proj_qs,
        "Volume": proj_volume,
        "Penetration": proj_penetration,
        "Closing Rate": proj_closing_rate,
        "VPG": proj_vpg,
        "Average Price": proj_avg_price,
    }


def calculate_variances(projection_dict, target_dict):
    return {
        "Arrivals": projection_dict["Arrivals"] - target_dict["Arrivals"],
        "Contracts": projection_dict["Contracts"] - target_dict["Contracts"],
        "Qs": projection_dict["Qs"] - target_dict["Qs"],
        "Volume": projection_dict["Volume"] - target_dict["Volume"],
        "Penetration": projection_dict["Penetration"] - target_dict["Penetration"],
        "Closing Rate": projection_dict["Closing Rate"] - target_dict["Closing Rate"],
        "VPG": projection_dict["VPG"] - target_dict["VPG"],
        "Average Price": projection_dict["Average Price"] - target_dict["Average Price"],
    }
