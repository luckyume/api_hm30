from fastapi import APIRouter, HTTPException

from app.services.hm30_monitor import HM30Monitor
from app.services.power_controller import PowerController


router = APIRouter()


# ==========================================
# SERVICES
# ==========================================

power_controller = PowerController()
hm30_monitor = HM30Monitor()


# ==========================================
# ROOT
# ==========================================

@router.get("/")
def root():

    return {
        "status": "online",
        "service": "Drone Control API",
    }


# ==========================================
# HEALTH
# ==========================================

@router.get("/health")
def health():

    power_status = (
        power_controller.status()
    )

    hm30_status = (
        hm30_monitor.get_status()
    )

    return {
        "status": "ok",
        "power_controller": power_status,
        "hm30": hm30_status,
    }


# ==========================================
# HM30 ON
# ==========================================

@router.get("/on")
def turn_hm30_on():

    try:

        response = (
            power_controller.turn_on()
        )

        return {
            "status": "success",
            "command": "ON",
            "controller_response": response,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to turn HM30 ON",
                "error": str(exc),
            },
        )


# ==========================================
# HM30 OFF
# ==========================================

@router.get("/off")
def turn_hm30_off():

    try:

        response = (
            power_controller.turn_off()
        )

        return {
            "status": "success",
            "command": "OFF",
            "controller_response": response,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to turn HM30 OFF",
                "error": str(exc),
            },
        )


# ==========================================
# POWER TEST
# ==========================================

@router.get("/test")
def test_power_controller():

    try:

        response = (
            power_controller.test()
        )

        return {
            "status": "success",
            "command": "TEST",
            "controller_response": response,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "Power controller test failed"
                ),
                "error": str(exc),
            },
        )


# ==========================================
# HM30 STATUS
# ==========================================

@router.get("/hm30/status")
def hm30_status():

    return hm30_monitor.get_status()