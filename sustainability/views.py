import os, time, re
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

ENERGY_FILE = getattr(settings, "SUSTAINABILITY_ENERGY_FILE", "/proc/energy/cgroup")

@staff_member_required
def monitor_page(request):
    return render(request, "sustainability/monitor.html", {
        "energy_file": ENERGY_FILE,
    })

def _parse_energy_file(content: str):
    """
    Parses lines of 'key=value' tokens. Requires pid, comm, energy (microjoules).
    Returns list of dicts with energy converted to kWh.
    """
    entries = []
    for raw_line in content.strip().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        kv = {}
        for k, v in re.findall(r"(\w+)=([^\s]+)", line):
            k = k.lower()
            if v.replace('.', '', 1).isdigit() or (v.startswith('-') and v[1:].replace('.', '', 1).isdigit()):
                try:
                    v = float(v) if ('.' in v) else int(v)
                except ValueError:
                    pass
            kv[k] = v
        if {"pid", "comm", "energy"}.issubset(kv.keys()):
            try:
                energy_uJ = float(kv["energy"])
                energy_kWh = energy_uJ * 2.7777777777778e-13  # µJ -> kWh
            except Exception:
                energy_kWh = None
            entries.append({
                "pid": int(kv["pid"]),
                "comm": str(kv["comm"]),
                "energy": energy_kWh,
                "all": kv,
                "raw": raw_line,
            })
    return entries

@staff_member_required
@require_POST
@csrf_protect
def ajax_get_energy(request):
    file_path = ENERGY_FILE

    if not os.path.isabs(file_path) or len(file_path) > 512 or ".." in file_path:
        return JsonResponse({"success": False, "data": {"message": "Invalid file path"}}, status=400)

    if not os.path.exists(file_path):
        return JsonResponse({"success": False, "data": {"message": f"File not found: {file_path}"}}, status=404)

    if not os.access(file_path, os.R_OK):
        return JsonResponse({"success": False, "data": {"message": f"File not readable: {file_path}"}}, status=403)

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception as e:
        return JsonResponse({"success": False, "data": {"message": f"Unable to read: {file_path}"}}, status=500)

    entries = _parse_energy_file(content)
    if not entries:
        return JsonResponse({
            "success": False,
            "data": {
                "message": "Could not parse any entries (expected lines of key=value with pid, comm, energy).",
                "raw": content
            }
        }, status=422)

    return JsonResponse({
        "success": True,
        "data": {
            "timestamp": int(time.time()),
            "file": file_path,
            "raw": content,
            "entries": entries
        }
    })
