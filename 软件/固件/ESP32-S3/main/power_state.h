#pragma once
#include <stdbool.h>
#include <stdint.h>

typedef enum { LOS_POWER_OFF, LOS_POWER_BOOTING, LOS_POWER_RUN, LOS_POWER_SLEEP, LOS_POWER_RESCUE } los_power_state_t;
typedef enum { LOS_KEY_NONE, LOS_KEY_TAP, LOS_KEY_SHORT, LOS_KEY_LONG, LOS_KEY_INVALID } los_key_event_t;

typedef struct { los_power_state_t state; bool usb_inserted_during_press; } los_power_machine_t;

void los_power_machine_init(los_power_machine_t *machine, los_power_state_t state);
los_key_event_t los_key_classify(uint32_t duration_ms);
void los_power_usb_inserted(los_power_machine_t *machine, bool key_pressed);
los_power_state_t los_power_release(los_power_machine_t *machine, uint32_t duration_ms, bool usb_present);
