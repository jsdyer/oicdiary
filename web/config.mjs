export default {
  "title": "Order in Council Diary",
  "intro": "Read the cabinet decisions hiding in plain sight. Search orders, appointments, departments and enabling statutes, then follow what changed.",
  "eyebrow": "FEDERAL CABINET / ORDERS IN COUNCIL",
  "accent": "#795638",
  "tint": "#f1e9df",
  "method": [
    "The official searchable database covers 1990 onward. This initial index collects orders approved in the current calendar year through collection day. Its coverage is explicit; the wider official archive remains linked.",
    "Extraction uses the database’s ordinary public search form and paginated results with a session cookie. It does not use an undocumented private endpoint or bypass access controls.",
    "The weekly snapshot diary and RSS feed show additions, changed entries and absences from the selected source results. A newly observed order may have an earlier approval date. First capture establishes a baseline.",
    "Some orders are not published because of statutory restrictions. This index reflects the public source and cannot establish the full set of cabinet decisions."
  ],
  "id": "oicdiary",
  "explorer-title": "Follow the record.",
  "cadence": "Weekly automated collection. Source dates and capture dates are shown separately.",
  "facets": [
    {
      "key": "department",
      "label": "Department"
    },
    {
      "key": "statute",
      "label": "Enabling statute"
    },
    {
      "key": "year",
      "label": "Approval year"
    }
  ],
  "columns": [
    {
      "key": "title",
      "label": "Order / subject"
    },
    {
      "key": "order",
      "label": "Order number"
    },
    {
      "key": "date",
      "label": "Approval date"
    },
    {
      "key": "department",
      "label": "Department"
    },
    {
      "key": "statute",
      "label": "Enabling statute"
    }
  ],
  "related": [
    {
      "label": "The Briefing Room",
      "url": "https://coolcode.ca/briefings/"
    },
    {
      "label": "What the Minister Was Prepared to Say",
      "url": "https://coolcode.ca/ministersays/"
    },
    {
      "label": "ATIP Decision Lens",
      "url": "https://coolcode.ca/atipdecisions/"
    }
  ]
};
