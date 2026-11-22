#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define LOS_PROTOCOL_VERSION 1U
#define LOS_PROTOCOL_SOF 0xA5U
#define LOS_PROTOCOL_MAX_PAYLOAD 64U
#define LOS_PROTOCOL_HEADER_SIZE 7U
#define LOS_PROTOCOL_CRC_SIZE 2U
#define LOS_PROTOCOL_MAX_FRAME (LOS_PROTOCOL_HEADER_SIZE + LOS_PROTOCOL_MAX_PAYLOAD + LOS_PROTOCOL_CRC_SIZE)

typedef enum {
    LOS_CMD_GET_POWER = 0x01,
    LOS_CMD_SET_POWER = 0x02,
    LOS_CMD_BUTTON_EVENT = 0x10,
    LOS_CMD_USB_EVENT = 0x11,
} los_command_t;

typedef enum {
    LOS_STATUS_OK = 0,
    LOS_STATUS_BAD_REQUEST = 1,
    LOS_STATUS_RETRY = 2,
    LOS_STATUS_UNAUTHORIZED = 3,
} los_status_t;

typedef struct {
    uint8_t sequence;
    uint8_t attempts;
    uint32_t timeout_ms;
} los_retry_policy_t;

typedef struct {
    uint8_t last_sequence;
    bool initialized;
} los_sequence_tracker_t;

typedef struct {
    uint8_t command;
    uint8_t sequence;
    const uint8_t *payload;
    uint16_t payload_length;
} los_frame_t;

uint16_t los_crc16(const uint8_t *data, size_t length);
size_t los_frame_encode(const los_frame_t *frame, uint8_t *out, size_t capacity);
int los_frame_decode(const uint8_t *data, size_t length, los_frame_t *out,
                    uint8_t *payload, size_t payload_capacity);
bool los_sequence_is_duplicate(los_sequence_tracker_t *tracker, uint8_t sequence);
bool los_retry_allowed(const los_retry_policy_t *policy, uint8_t attempt);
