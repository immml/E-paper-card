// SPDX-License-Identifier: AGPL-3.0-or-later
#include "esp_chip_info.h"
#include "esp_heap_caps.h"
#include "esp_log.h"

void app_main(void)
{
    esp_chip_info_t chip;
    esp_chip_info(&chip);
    ESP_LOGI("lighting_os", "lighting OS Firmware | %s | cores=%u | revision=%u",
             CONFIG_IDF_TARGET, (unsigned)chip.cores, (unsigned)chip.revision);
    ESP_LOGI("lighting_os", "PSRAM heap: %zu bytes",
             heap_caps_get_total_size(MALLOC_CAP_SPIRAM));
}
