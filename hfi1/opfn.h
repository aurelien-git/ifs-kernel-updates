/*
 * Copyright(c) 2016 Intel Corporation.
 *
 * This file is provided under a dual BSD/GPLv2 license.  When using or
 * redistributing this file, you may do so under either license.
 *
 * GPL LICENSE SUMMARY
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of version 2 of the GNU General Public License as
 * published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * BSD LICENSE
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *  - Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *  - Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 *  - Neither the name of Intel Corporation nor the names of its
 *    contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */
#ifndef _HFI1_OPFN_H
#define _HFI1_OPFN_H

/* STL Verbs Extended */
#define IB_BTHE_E_SHIFT           24
#define IB_BTHE_E                 BIT(IB_BTHE_E_SHIFT)
#define HFI1_VERBS_E_ATOMIC_VADDR U64_MAX

/* OPFN flags */
#define HFI1_S_STL_E_SENDING     0x1
#define HFI1_S_STL_E_PENDING     0x2

static inline bool hfi1_opfn_extended(u32 bth1)
{
	return !!(bth1 & IB_BTHE_E);
}

struct ib_atomic_eth;

enum hfi1_opfn_codes {
	STL_VERBS_EXTD_NONE = 0,
	STL_VERBS_EXTD_TID_RDMA,
	STL_VERBS_EXTD_MAX
};

struct hfi1_opfn_data {
	bool extended;
	u16 requested;
	u16 completed;
	enum hfi1_opfn_codes curr;
	/* serialize opfn function calls */
	spinlock_t lock;
	struct work_struct opfn_work;
};

/* WR opcode for OPFN */
#define IB_WR_OPFN IB_WR_RESERVED3

#define OPFN_CODE(code) BIT((code - 1))
#define OPFN_MASK(code) OPFN_CODE(STL_VERBS_EXTD_##code)

void opfn_conn_request(struct rvt_qp *qp);
void opfn_send_conn_request(struct work_struct *work);
void opfn_schedule_conn_request(struct rvt_qp *qp);
void opfn_conn_response(struct rvt_qp *qp, struct rvt_ack_entry *e,
			struct ib_atomic_eth *ateth);
void opfn_conn_reply(struct rvt_qp *qp, u64 data);
void opfn_conn_error(struct rvt_qp *qp);

#endif /* _HFI1_OPFN_H */
