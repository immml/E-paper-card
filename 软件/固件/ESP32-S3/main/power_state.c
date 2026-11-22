#include "power_state.h"

void los_power_machine_init(los_power_machine_t *machine, los_power_state_t state)
{
    machine->state = state;
    machine->usb_inserted_during_press = false;
}

los_key_event_t los_key_classify(uint32_t duration_ms)
{
    if (duration_ms < 200) return LOS_KEY_TAP;
    if (duration_ms <= 1500) return LOS_KEY_SHORT;
    if (duration_ms <= 2000) return LOS_KEY_INVALID;
    return LOS_KEY_LONG;
}

void los_power_usb_inserted(los_power_machine_t *machine, bool key_pressed)
{
    if (key_pressed && machine->state == LOS_POWER_OFF) machine->usb_inserted_during_press = true;
}

los_power_state_t los_power_release(los_power_machine_t *machine, uint32_t duration_ms, bool usb_present)
{
    los_key_event_t event = los_key_classify(duration_ms);
    if (machine->state == LOS_POWER_OFF) {
        if (machine->usb_inserted_during_press) {
            machine->usb_inserted_during_press = false;
            machine->state = usb_present ? LOS_POWER_RESCUE : LOS_POWER_OFF;
        } else if (event == LOS_KEY_LONG) {
            machine->state = LOS_POWER_BOOTING;
        }
    } else if (machine->state == LOS_POWER_RUN) {
        if (event == LOS_KEY_SHORT) machine->state = LOS_POWER_SLEEP;
        else if (event == LOS_KEY_LONG) machine->state = LOS_POWER_OFF;
    } else if (machine->state == LOS_POWER_SLEEP && event == LOS_KEY_LONG) {
        machine->state = LOS_POWER_RUN;
    }
    return machine->state;
}
