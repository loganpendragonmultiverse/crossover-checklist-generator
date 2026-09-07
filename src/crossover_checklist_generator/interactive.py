"""Author-supplied graph constraints and a round-trip local checklist."""

from __future__ import annotations

import json
from typing import Any


def enrich(issues: list[dict[str, Any]], choices: dict[str, str]) -> list[str]:
    by_id = {item["id"]: item for item in issues}
    options: dict[str, set[str]] = {}
    for item in issues:
        group, branch = item.get("branch_group"), item.get("branch")
        if bool(group) != bool(branch) or (
            group and (not isinstance(group, str) or not isinstance(branch, str))
        ):
            raise ValueError("branch_group and branch must both be non-empty text")
        if group:
            assert isinstance(branch, str)
            options.setdefault(group, set()).add(branch)
        prerequisites = item["prerequisites"]
        if not isinstance(prerequisites, list) or any(
            not isinstance(p, str) or p not in by_id for p in prerequisites
        ):
            raise ValueError(f"{item['id']}: prerequisites must reference known issue IDs")
    for group, selected in choices.items():
        if selected not in options.get(group, set()):
            raise ValueError(f"Unknown branch choice {group}={selected}")
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(identifier: str) -> None:
        if identifier in visiting:
            raise ValueError(f"Prerequisite cycle at {identifier}")
        if identifier in visited:
            return
        visiting.add(identifier)
        for prerequisite in by_id[identifier]["prerequisites"]:
            visit(prerequisite)
        visiting.remove(identifier)
        visited.add(identifier)

    for item in issues:
        visit(item["id"])
        item["selected"] = (
            not item.get("branch_group")
            or item["branch_group"] not in choices
            or choices[item["branch_group"]] == item["branch"]
        )
    warnings = []
    for item in issues:
        for prerequisite in item["prerequisites"]:
            if item["selected"] and not by_id[prerequisite]["selected"]:
                warnings.append(f"{item['id']} requires excluded branch issue {prerequisite}")
            elif by_id[prerequisite]["position"] >= item["position"]:
                warnings.append(
                    f"{item['id']} precedes its prerequisite {prerequisite}; author order preserved"
                )
    return warnings


def render_html(report: dict[str, Any]) -> str:
    payload = json.dumps(report).replace("<", "\\u003c").replace("&", "\\u0026")
    return (
        """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Crossover checklist</title>
<style>body{font:17px system-ui;max-width:950px;margin:auto;padding:22px;background:#f5f1e8;color:#203442}article{background:white;padding:18px;border:1px solid #abc;border-radius:10px;margin:15px 0}label{display:block;margin:10px 0}select,textarea,button{font:inherit;padding:10px;max-width:100%;box-sizing:border-box}textarea{width:100%}p{overflow-wrap:anywhere}progress{width:100%}</style>
<h1 id="title"></h1><p>Author order is preserved. Progress edits stay in this page until you download a new input. All alternative branches remain in the export.</p>
<progress id="progress" aria-label="Selected issue progress"></progress><p id="status" role="status"></p><ul id="warnings"></ul><main id="issues"></main><button id="download">Download edited checklist</button>
<script type="application/json" id="data">"""
        + payload
        + """</script><script>
const data=JSON.parse(document.getElementById('data').textContent);document.getElementById('title').textContent=data.title;
const cards=[];for(const warning of data.warnings){const li=document.createElement('li');li.textContent=warning;document.getElementById('warnings').append(li);}
for(const item of data.issues){const card=document.createElement('article');const h=document.createElement('h2');h.textContent=item.position+'. '+item.series+' #'+item.issue;card.append(h);
const context=document.createElement('p');context.textContent=item.section+(item.branch_group?' · '+item.branch_group+': '+item.branch:'')+(item.selected?'':' · excluded by selected branch');card.append(context);
const label=document.createElement('label');label.textContent='Progress';const select=document.createElement('select');for(const status of ['pending','read','skipped']){const o=document.createElement('option');o.textContent=status;o.value=status;select.append(o);}select.value=item.status;select.addEventListener('change',()=>{item.status=select.value;refresh();});label.append(select);card.append(label);
const notes=document.createElement('label');notes.textContent='Private note';const text=document.createElement('textarea');text.value=item.note??'';text.addEventListener('input',()=>item.note=text.value);notes.append(text);card.append(notes);
const dependencies=document.createElement('p');card.append(dependencies);cards.push([item,dependencies]);document.getElementById('issues').append(card);}
function refresh(){const selected=data.issues.filter(i=>i.selected),done=selected.filter(i=>i.status==='read').length;progress.max=selected.length||1;progress.value=done;document.getElementById('status').textContent=done+' of '+selected.length+' selected issues read';
for(const [item,p] of cards){const pending=item.prerequisites.filter(id=>data.issues.find(i=>i.id===id).status!=='read');p.textContent=pending.length?'Prerequisites not read: '+pending.join(', '):'No unread prerequisites';}}
const progress=document.getElementById('progress');document.getElementById('download').addEventListener('click',()=>{const sections=[];for(const item of data.issues){let section=sections.find(s=>s.index===item.section_index);if(!section){section={index:item.section_index,title:item.section,entries:[]};sections.push(section);}const entry={series:item.series,issue:item.issue,status:item.status,note:item.note??'',prerequisites:item.prerequisites};if(item.branch_group){entry.branch_group=item.branch_group;entry.branch=item.branch;}section.entries.push(entry);}
const output={version:1,title:data.title,branch_choices:data.branch_choices,sections:sections.map(({index,...s})=>s)};const url=URL.createObjectURL(new Blob([JSON.stringify(output,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='edited-crossover.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});refresh();</script></html>"""
    )
