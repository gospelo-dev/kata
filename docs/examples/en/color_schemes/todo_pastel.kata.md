# <span data-kata="p-title">Weekend Shopping List</span>

| # | Task | Status |
|:-:|------|:------:|
| <span data-kata="p-items-0-id">1</span> | <span data-kata="p-items-0-task">Buy milk</span> | <span data-kata="p-items-0-status" data-kata-enum="done">done</span> |
| <span data-kata="p-items-1-id">2</span> | <span data-kata="p-items-1-task">Buy bread</span> | <span data-kata="p-items-1-status" data-kata-enum="done">done</span> |
| <span data-kata="p-items-2-id">3</span> | <span data-kata="p-items-2-task">Buy eggs</span> | <span data-kata="p-items-2-status" data-kata-enum="todo">todo</span> |
| <span data-kata="p-items-3-id">4</span> | <span data-kata="p-items-3-task">Buy soy sauce</span> | <span data-kata="p-items-3-status" data-kata-enum="todo">todo</span> |


Total: <span data-kata="p-items">4</span> tasks
<style>
table { table-layout: fixed; width: 100%; display: table !important; overflow: visible !important; }
table th, table td { overflow-wrap: break-word; word-break: break-word; vertical-align: top; }
.markdown-preview { max-width: 100% !important; padding-left: 2em !important; padding-right: 2em !important; }
[data-kata-enum] { display: inline-block; padding: 1px 6px; border-radius: 4px; font-size: 0.9em; }
[data-kata-enum="done"] { background: #eaefec; color: #7a8a80; }
[data-kata-enum="todo"] { background: #a8e6c4; color: #1a5c3a; }
</style>

---

<details>
<summary>Specification</summary>

**Prompt**

```yaml
This template generates a simple TODO list.
items contains tasks with id, task description, and status.
status is either todo or done.
```

**Template**

```kata:template
# {{ title }}

| # | Task | Status |
|:-:|------|:------:|
{% for item in items %}| {{ item.id }} | {{ item.task }} | {{ item.status }} |
{% endfor %}

Total: {{ items | length }} tasks
```

**Schema**

```yaml
title: string!
items[]!:
  id: string!
  task: string!
  status: enum(todo, done)
```

<!-- kata-structure-integrity: sha256:9ee46029de89a6ce1a7fe36a8bd37e05cc5001af77ec882333d6c6b4df486592 -->
</details>

<details>
<summary>Style</summary>

```yaml
colorScheme: pastel
```

</details>
<details>
<summary>Data</summary>

```yaml
title: Weekend Shopping List
items:
- id: '1'
  task: Buy milk
  status: done
- id: '2'
  task: Buy bread
  status: done
- id: '3'
  task: Buy eggs
  status: todo
- id: '4'
  task: Buy soy sauce
  status: todo
```

</details>