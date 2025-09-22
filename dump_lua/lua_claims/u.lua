local p = {}

local langcode = mw.getCurrentFrame():callParserFunction('int', { 'lang' })

--[[
Lua error: bad argument #1 to 'isKnownLanguageTag' (string expected, got table).

if langcode and mw.language.isKnownLanguageTag(langcode) then
    p.lang = mw.language.new(langcode).code
else
    p.lang = mw.language.getContentLanguage().code
end
]]

p.lang = mw.language.getContentLanguage().code

local mf = require('Module:Formatnum')

local function formatNum(number)
    if not number or number == "" then return "" end
    return mf.formatNum(number, p.lang)
end

local function format_diff(new_val, old_val)
    if new_val == nil or old_val == nil then
        return "-"
    end
    local diff = new_val - old_val
    if diff == 0 then
        return "-"
    elseif diff > 0 then
        return "+" .. formatNum(diff)
    else
        return formatNum(diff)
    end
end

local function make_numbers(props, old_data)
    local lines = {}

    table.insert(lines, "== Numbers ==")
    table.insert(lines, '{| class="wikitable mw-collapsible mw-collapsed sortable"')
    table.insert(lines, "|-")
    table.insert(lines, "! # !! Property!! Claims !! Diff")

    local idx = 1
    for _, prop in ipairs(props) do
        local pid = prop.pid
        local pdata = prop.data
        local old_pdata = old_data.properties[pid]
        local diff_claims = format_diff(pdata.property_claims_count, old_pdata.property_claims_count)

        table.insert(lines, "|-")
        table.insert(lines,
            "| " ..
            idx .. " || {{P|" .. pid .. "}} || " .. formatNum(pdata.property_claims_count) .. " || " .. diff_claims)

        idx = idx + 1
    end

    table.insert(lines, "|-")
    table.insert(lines, "! 101")
    table.insert(lines, "! others || 0 || -")
    table.insert(lines, "|}")

    return table.concat(lines, "\n")
end

local function make_status(new_data, old_data, old_date, new_date)
    local texts = {
        all_items = "Total items",
        items_missing_P31 = "Items without P31",
        items_with_0_claims = "Items without claims",
        items_with_1_claim = "Items with 1 claim only",
        total_claims_count = "Total number of claims",
        total_properties_count = "Number of properties in the report"
    }

    local keys_order = {
        "all_items",
        "items_missing_P31",
        "items_with_0_claims",
        "items_with_1_claim",
        "total_claims_count",
        "total_properties_count"
    }

    local lines = {}
    table.insert(lines, '{| class="wikitable sortable"')

    table.insert(lines, (
        "! Title !! [[User:Mr. Ibrahem/claims/%s.json|%s]] !! [[User:Mr. Ibrahem/claims/%s.json|%s]] !! Diff"
    ):format(
        old_data.date,
        old_date,
        new_data.date,
        new_date
    ))

    table.insert(lines, "|-")

    for _, key in ipairs(keys_order) do
        local label = texts[key]
        local old_value = old_data[key]
        local new_value = new_data[key]
        local diff = (key == "total_properties_count") and "-" or format_diff(new_value, old_value)

        table.insert(lines,
            ("| %s || %s || %s || %s"):format(label, formatNum(old_value), formatNum(new_value), diff)
        )
        table.insert(lines, "|-")
    end

    lines[#lines] = "|}"

    return table.concat(lines, "\n")
end

local function make_qids_table(pdata, old_pdata)
    local sorted_qids = {}
    for qid, num in pairs(pdata.qids) do
        table.insert(sorted_qids, { qid = qid, num = num })
    end
    table.sort(sorted_qids, function(a, b) return a.num > b.num end)

    local lines = {}
    table.insert(lines, '=== QIDs ===')
    table.insert(lines, '{| class="wikitable mw-collapsible mw-collapsed sortable plainrowheaders"')
    table.insert(lines, "|-")
    table.insert(lines, '! class="sortable" | #')
    table.insert(lines, '! class="sortable" | QID')
    table.insert(lines, '! class="sortable" | Count')
    table.insert(lines, '! class="sortable" | Diff')

    local qidx = 1
    for _, q in ipairs(sorted_qids) do
        local old_num = old_pdata.qids and old_pdata.qids[q.qid] or 0
        table.insert(lines, "|-")
        table.insert(lines, "! " .. qidx)
        -- table.insert(lines, "| {{Q|" .. q.qid .. "}}")
        table.insert(lines, "| [[" .. q.qid .. "]]")
        table.insert(lines, "| " .. formatNum(q.num))
        table.insert(lines, "| " .. format_diff(q.num, old_num))
        qidx = qidx + 1
    end

    local old_others = old_pdata.qids_others or 0
    local new_others = pdata.qids_others or 0
    table.insert(lines, "|-")
    table.insert(lines, "! " .. qidx)
    table.insert(lines, "! others")
    table.insert(lines, "! " .. formatNum(new_others))
    table.insert(lines, "! " .. format_diff(new_others, old_others))

    table.insert(lines, "|}")
    return table.concat(lines, "\n")
end

local function make_property_status(pid, pdata, old_pdata)
    local texts = {
        items_with_property = "Total items using this property",
        property_claims_count = "Total number of claims",
        unique_qids_count = "Number of unique QIDs"
    }

    local lines = {}
    table.insert(lines, "== {{P|" .. pid .. "}} ==")
    table.insert(lines, '{| class="wikitable sortable"')
    table.insert(lines, "! Title !! Number !! Diff")
    table.insert(lines, "|-")

    local keys_order = {
        "items_with_property",
        "property_claims_count",
        "unique_qids_count"
    }

    for _, key in ipairs(keys_order) do
        local label = texts[key]
        local old_value = old_pdata[key]
        local new_value = pdata[key]
        local diff = format_diff(new_value, old_value)

        table.insert(lines, ("| %s || %s || %s"):format(label, formatNum(new_value), diff))
        table.insert(lines, "|-")
    end

    lines[#lines] = "|}"

    return table.concat(lines, "\n")
end

local function make_sections(props, old_data)
    local lines = {}

    for _, prop in ipairs(props) do
        local pid = prop.pid
        local pdata = prop.data
        local old_pdata = old_data.properties[pid]

        table.insert(lines, make_property_status(pid, pdata, old_pdata))

        if pdata.qids then
            table.insert(lines, make_qids_table(pdata, old_pdata))
        end
    end

    return table.concat(lines, "\n{{clear}}\n")
end

local function _report(old_date, new_date)
    local old_data = mw.loadJsonData("User:Mr. Ibrahem/claims/" .. old_date .. ".json")
    local new_data = mw.loadJsonData("User:Mr. Ibrahem/claims/" .. new_date .. ".json")

    local props = {}
    for pid, pdata in pairs(new_data.properties) do
        table.insert(props, { pid = pid, claims = pdata.property_claims_count, data = pdata })
    end

    table.sort(props, function(a, b)
        return a.claims > b.claims
    end)

    local status = make_status(new_data, old_data, old_date, new_date)
    local numbers = make_numbers(props, old_data)
    local sections = make_sections(props, old_data)

    return ("%s\n\n%s\n\n%s"):format(status, numbers, sections)
end

function p.report(frame)
    local text = _report("2025-04-23", "2025-09-03")
    return frame:preprocess(text)
end

function p.report_by_date(frame)
    local text = _report(frame.args.old, frame.args.new)
    return frame:preprocess(text)
end

return p
