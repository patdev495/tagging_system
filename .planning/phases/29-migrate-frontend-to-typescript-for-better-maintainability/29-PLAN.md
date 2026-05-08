# Phase 29: Migrate frontend to TypeScript - Plan

**Phase:** 29
**Goal:** Chuyển đổi toàn bộ mã nguồn frontend_v2 sang TypeScript để cải thiện khả năng bảo trì và giảm thiểu lỗi runtime.

<frontmatter>
wave: 1
depends_on: []
files_modified:
  - frontend_v2/package.json
  - frontend_v2/tsconfig.json
  - frontend_v2/vite.config.js
autonomous: true
</frontmatter>

## Wave 1: Infrastructure & Environment

<task>
<read_first>
- frontend_v2/package.json
- frontend_v2/vite.config.js
</read_first>
<action>
1. Cài đặt các devDependencies cần thiết: `typescript`, `vue-tsc`, `@types/node`.
2. Tạo file `tsconfig.json` với cấu hình strict mode (D-02).
3. Đổi tên `vite.config.js` thành `vite.config.ts`.
4. Cập nhật scripts trong `package.json`: thêm bước type-check vào build.
</action>
<acceptance_criteria>
- `frontend_v2/package.json` chứa `"typescript"`, `"vue-tsc"` trong devDependencies.
- `frontend_v2/package.json` script `"build"` có tiền tố `"vue-tsc --noEmit &&"`.
- `frontend_v2/tsconfig.json` tồn tại với `"strict": true`.
- `frontend_v2/vite.config.ts` tồn tại và cấu hình Tailwind v4 vẫn hoạt động.
</acceptance_criteria>
</task>

<frontmatter>
wave: 2
depends_on: [1]
files_modified:
  - frontend_v2/src/main.ts
  - frontend_v2/src/core/api.ts
  - frontend_v2/src/core/router/index.ts
  - frontend_v2/src/core/stores/*.ts
  - frontend_v2/src/types/index.ts
autonomous: true
</frontmatter>

## Wave 2: Core logic & Global state

<task>
<read_first>
- frontend_v2/src/main.js
- frontend_v2/src/core/api.js
- frontend_v2/src/core/router/index.js
- frontend_v2/src/core/stores/system.js
- frontend_v2/src/core/stores/settings.js
</read_first>
<action>
1. Rename các file `.js` trong `src/core/` và `src/` sang `.ts`.
2. Migrate `main.ts`: Khai báo types cho app instance.
3. Migrate `core/api.ts`: Khai báo types cho Axios response/request interceptors.
4. Migrate stores (`system.ts`, `settings.ts`): Define `State`, `Getters`, `Actions` interfaces cho Pinia.
5. Tạo `src/types/api.ts` để chứa các shared interfaces cho backend responses.
</action>
<acceptance_criteria>
- Các file `.js` tương ứng được đổi tên thành `.ts`.
- Không còn `any` trong các function signatures quan trọng của API và Stores.
- `npm run build` (hoặc `vue-tsc`) không báo lỗi ở các file này.
</acceptance_criteria>
</task>

<frontmatter>
wave: 3
depends_on: [2]
files_modified:
  - frontend_v2/src/features/*/api.ts
  - frontend_v2/src/features/packing/composables/useScanLogic.ts
autonomous: true
</frontmatter>

## Wave 3: Feature APIs & Composables

<task>
<read_first>
- frontend_v2/src/features/packing/api.js
- frontend_v2/src/features/catalog/api.js
- frontend_v2/src/features/packing/composables/useScanLogic.js
</read_first>
<action>
1. Rename và migrate các file API của feature (`packing`, `catalog`, `history`, `print`).
2. Khai báo types cho dữ liệu Customer, Product, Carton, ScanItem.
3. Migrate `useScanLogic.ts`: Đây là core logic phức tạp nhất, cần khai báo types chặt chẽ cho scan buffer và các ref states.
</action>
<acceptance_criteria>
- Feature APIs trả về typed Promises (e.g., `Promise<Customer[]>`).
- `useScanLogic.ts` sử dụng `ref<T>()` và `computed<T>()` với explicit types.
- Toàn bộ business logic trong composable được type-checked.
</acceptance_criteria>
</task>

<frontmatter>
wave: 4
depends_on: [3]
files_modified:
  - frontend_v2/src/**/*.vue
autonomous: true
</frontmatter>

## Wave 4: Vue Components Migration (Bulk)

<task>
<read_first>
- frontend_v2/src/views/PackingPage.vue
- frontend_v2/src/features/packing/components/ScannedList.vue
- frontend_v2/src/core/components/AppHeader.vue
</read_first>
<action>
1. Thêm `lang="ts"` vào thẻ `<script setup>` của tất cả file `.vue`.
2. Migrate `defineProps` và `defineEmits` sang type-based declaration (D-03).
3. Sửa các lỗi type mismatch khi truyền props giữa các component.
4. Ưu tiên migrate các component lớn trước (`PackingPage.vue`, `ScannedList.vue`).
</action>
<acceptance_criteria>
- Tất cả component có `lang="ts"` trong `<script setup>`.
- `defineProps` sử dụng Generic syntax (e.g., `defineProps<{ item: Product }>()`).
- Project build thành công với `vue-tsc --noEmit`.
</acceptance_criteria>
</task>

## Verification & Must-Haves

### Must-Haves
- **M-01:** Project phải build thành công với lệnh `npm run build`.
- **M-02:** Mọi file logic (.ts) phải pass strict type checking (không dùng `any` bừa bãi).
- **M-03:** Các tính năng cũ (Packing, Admin) phải hoạt động bình thường trên trình duyệt.

### Verification Criteria
- [ ] Chạy `npm run dev` và verify không có lỗi runtime trong console.
- [ ] Chạy `npx vue-tsc --noEmit` và verify output trống (0 errors).
- [ ] Thực hiện một chu kỳ đóng gói test (Select Product -> Scan -> Print) để đảm bảo logic không bị broke.
