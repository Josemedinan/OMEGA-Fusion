#pragma once
#include <stdint.h>
#define OMEGA_BASE 0x40000000u
#define OMEGA_CTRL     0x000u
#define OMEGA_STATUS   0x004u
#define OMEGA_DMA_SRC  0x008u
#define OMEGA_CAPS     0x00cu
#define OMEGA_A(i)    (0x100u + 4u*(i))
#define OMEGA_B(i)    (0x200u + 4u*(i))
#define OMEGA_C(i)    (0x300u + 4u*(i))
#define OMEGA_START     (1u<<0)
#define OMEGA_INT4      (1u<<1)
#define OMEGA_DMA_START (1u<<2)
#define OMEGA_CLEAR     (1u<<3)
#define OMEGA_BUSY      (1u<<0)
#define OMEGA_DONE      (1u<<1)
#define OMEGA_ERROR     (1u<<2)
static inline void omega_write(uint32_t off,uint32_t val) {
    *(volatile uint32_t *)(uintptr_t)(OMEGA_BASE+off)=val;
}
static inline uint32_t omega_read(uint32_t off) {
    return *(volatile uint32_t *)(uintptr_t)(OMEGA_BASE+off);
}
// Assumes an external SoC maps this peripheral at OMEGA_BASE.
static inline int omega_multiply_tile(const int8_t *a,const int8_t *b,
                                      int32_t *c,int int4,unsigned max_poll) {
    omega_write(OMEGA_CTRL,OMEGA_CLEAR);
    for(unsigned i=0;i<16;i++) {
        omega_write(OMEGA_A(i),(uint8_t)a[i]);
        omega_write(OMEGA_B(i),(uint8_t)b[i]);
    }
    omega_write(OMEGA_CTRL,OMEGA_START|(int4?OMEGA_INT4:0));
    for(unsigned i=0;i<max_poll;i++) {
        uint32_t status=omega_read(OMEGA_STATUS);
        if(status&OMEGA_ERROR) return -2;
        if(status&OMEGA_DONE) {
            for(unsigned j=0;j<16;j++)c[j]=(int32_t)omega_read(OMEGA_C(j));
            return 0;
        }
    }
    return -1;
}
