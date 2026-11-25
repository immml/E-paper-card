// SPDX-License-Identifier: AGPL-3.0-or-later
#include "esp_chip_info.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_ota_ops.h"
#include "esp_psram.h"
#include <stdlib.h>

static void verify_pending_image(void)
{
    const esp_partition_t *running = esp_ota_get_running_partition();
    esp_ota_img_states_t state;
    esp_err_t result = esp_ota_get_state_partition(running, &state);
    if (result == ESP_ERR_NOT_FOUND) {
        return;
    }
    if (result != ESP_OK) {
        ESP_LOGE("lighting_os", "OTA state for %s: %s", running->label, esp_err_to_name(result));
        return;
    }
    if (state != ESP_OTA_IMG_PENDING_VERIFY) {
        return;
    }

    bool healthy = esp_psram_is_initialized() && esp_psram_get_size() == 8U * 1024U * 1024U;
    volatile unsigned char *probe = healthy ? heap_caps_malloc(64, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT) : NULL;
    healthy = probe != NULL;
    if (probe != NULL) {
        for (unsigned i = 0; i < 64; ++i) {
            probe[i] = (unsigned char)(i ^ 0xa5U);
        }
        for (unsigned i = 0; i < 64; ++i) {
            if (probe[i] != (unsigned char)(i ^ 0xa5U)) {
                healthy = false;
                break;
            }
        }
        free((void *)probe);
    }
    if (!healthy) {
        ESP_LOGE("lighting_os", "Startup self-test failed on %s", running->label);
        result = esp_ota_mark_app_invalid_rollback_and_reboot();
        ESP_LOGE("lighting_os", "Rollback could not start: %s", esp_err_to_name(result));
        return;
    }
    result = esp_ota_mark_app_valid_cancel_rollback();
    if (result != ESP_OK) {
        ESP_LOGE("lighting_os", "OTA confirmation failed: %s", esp_err_to_name(result));
    } else {
        ESP_LOGI("lighting_os", "Confirmed OTA image on %s", running->label);
    }
}

void app_main(void)
{
    esp_chip_info_t chip;
    esp_chip_info(&chip);
    ESP_LOGI("lighting_os", "lighting OS Firmware | %s | cores=%u | revision=%u",
             CONFIG_IDF_TARGET, (unsigned)chip.cores, (unsigned)chip.revision);
    ESP_LOGI("lighting_os", "PSRAM heap: %zu bytes",
             heap_caps_get_total_size(MALLOC_CAP_SPIRAM));
    verify_pending_image();
}
