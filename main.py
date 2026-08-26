from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

from config.config import get_config
from schema.request import RequestSchema
from services.base import get_service


app = FastAPI()

provider_name = "saman"
config = get_config(provider=provider_name)
config.load_env_values()
service = get_service(config)


@app.post("/saman/pay")
async def create_payment(request_data: RequestSchema):  # this implemented just for saman
    
    try:
        token = await service.get_token(
            amount=request_data.amount,
            res_num=request_data.res_num
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Redirecting to Saman...</title></head>
    <body>
        <form id="samanForm" method="post" action="https://sep.shaparak.ir/OnlinePG/OnlinePG">
            <input type="hidden" name="Token" value="{token}">
            <input type="hidden" name="GetMethod" value="0">
        </form>
        <script>
            document.getElementById('samanForm').submit();
        </script>
        <p>در حال انتقال به درگاه بانک سامان...</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html)



@app.post("/callback")
async def callback(request: Request):
    """
    SEP posts the result here after payment
    """
    form = await request.form()
    data = dict(form)

    state = data.get("State") or data.get("state")
    status = data.get("Status") or data.get("status")
    ref_num = data.get("RefNum") or data.get("refNum")
    res_num = data.get("ResNum") or data.get("resNum")
    amount = data.get("Amount") or data.get("amount")
    trace_no = data.get("TraceNo") or data.get("traceNo")

    if str(status) not in ("0", "2") and str(state) not in ("OK", "0"):
        return JSONResponse({
            "success": False,
            "message": "Payment failed or cancelled",
            "raw": data
        })

    if not ref_num:
        return JSONResponse({
            "success": False,
            "message": "No RefNum received",
            "raw": data
        })

    try:
        verify_result = await service.verify_transaction(ref_num)
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Verify failed: {str(e)}",
            "raw": data
        })

    result_code = verify_result.get("ResultCode") or verify_result.get("resultCode")
    success = verify_result.get("Success") or verify_result.get("success")

    if success is True or str(result_code) == "0":
        # ===== SUCCESS =====
        # Here you should:
        # 1. Mark order as paid in your DB
        # 2. Prevent double-spending (check if RefNum already processed)
        return JSONResponse({
            "success": True,
            "message": "Payment verified successfully",
            "ref_num": ref_num,
            "res_num": res_num,
            "amount": amount,
            "trace_no": trace_no,
            "verify": verify_result
        })
    else:
        return JSONResponse({
            "success": False,
            "message": "Verification failed",
            "verify": verify_result,
            "raw": data
        })

@app.get("/")
async def root():
    return FileResponse("index.html")