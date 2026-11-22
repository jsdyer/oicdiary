import test from 'node:test';import assert from 'node:assert/strict';
import {analyse} from '../web/model.mjs';
test('approval grouping uses the order date, not capture time',()=>{const a=analyse([{department:'X',statute:'Act',date:'2026-01-01',captured_at:'2026-03-01'}]);assert.equal(a.panels[1].items[0].label,'2026-01');});
