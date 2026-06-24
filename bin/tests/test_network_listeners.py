import json
import runpy
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "network-listeners"


class NetworkListenersTest(unittest.TestCase):
    def load_module(self):
        return runpy.run_path(str(SCRIPT))

    def interface_index(self, module):
        payload = [
            {
                "ifname": "lo",
                "flags": ["LOOPBACK", "UP"],
                "link_type": "loopback",
                "addr_info": [{"family": "inet", "local": "127.0.0.1"}],
            },
            {
                "ifname": "enp5s0",
                "flags": ["BROADCAST", "UP", "LOWER_UP"],
                "link_type": "ether",
                "addr_info": [{"family": "inet", "local": "172.16.0.208"}],
            },
            {
                "ifname": "tailscale0",
                "flags": ["POINTOPOINT", "UP", "LOWER_UP"],
                "link_type": "none",
                "addr_info": [
                    {"family": "inet", "local": "100.122.168.47"},
                    {"family": "inet6", "local": "fd7a:115c:a1e0::253a:a82f"},
                ],
            },
            {
                "ifname": "br-test",
                "flags": ["BROADCAST", "UP"],
                "link_type": "ether",
                "addr_info": [{"family": "inet", "local": "172.18.0.1"}],
            },
        ]
        return module["parse_ip_addr_json"](json.dumps(payload))

    def test_splits_ipv4_ipv6_and_interface_scoped_binds(self):
        module = self.load_module()

        self.assertEqual(module["split_host_port"]("0.0.0.0:80"), ("0.0.0.0", "80", None))
        self.assertEqual(
            module["split_host_port"]("[fd7a:115c:a1e0::253a:a82f]:8080"),
            ("fd7a:115c:a1e0::253a:a82f", "8080", None),
        )
        self.assertEqual(
            module["split_host_port"]("0.0.0.0%virbr0:67"),
            ("0.0.0.0", "67", "virbr0"),
        )
        self.assertEqual(
            module["split_host_port"]("[fe80::d3f0:5af1:36b9:67c]%enp5s0:45100"),
            ("fe80::d3f0:5af1:36b9:67c", "45100", "enp5s0"),
        )

    def test_classifies_lan_tailscale_and_bridge_addresses_from_interfaces(self):
        module = self.load_module()
        interfaces = self.interface_index(module)

        self.assertEqual(module["classify_host"]("0.0.0.0", None, interfaces), "wildcard")
        self.assertEqual(module["classify_host"]("172.16.0.208", None, interfaces), "lan")
        self.assertEqual(module["classify_host"]("100.122.168.47", None, interfaces), "tailscale")
        self.assertEqual(
            module["classify_host"]("fd7a:115c:a1e0::253a:a82f", None, interfaces),
            "tailscale",
        )
        self.assertEqual(module["classify_host"]("172.18.0.1", None, interfaces), "bridge")

    def test_groups_tailscale_only_ignoring_loopback(self):
        module = self.load_module()
        interfaces = self.interface_index(module)
        listeners = [
            module["parse_ss_line"](
                'tcp LISTEN 0 4096 127.0.0.1:8080 0.0.0.0:* users:(("svc",pid=42,fd=3))',
                interfaces,
            ),
            module["parse_ss_line"](
                'tcp LISTEN 0 4096 100.122.168.47:8080 0.0.0.0:* users:(("svc",pid=42,fd=4))',
                interfaces,
            ),
        ]

        groups = module["group_listeners"](listeners)

        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].exposure, "tailscale-only")
        self.assertEqual(
            module["format_bindings"](groups[0].visible_listeners()),
            "100.122.168.47:8080",
        )

    def test_wildcard_takes_precedence_over_lan_and_tailscale(self):
        module = self.load_module()
        interfaces = self.interface_index(module)
        listeners = [
            module["parse_ss_line"](
                'tcp LISTEN 0 4096 0.0.0.0:443 0.0.0.0:* users:(("caddy",pid=7,fd=3))',
                interfaces,
            ),
            module["parse_ss_line"](
                'tcp LISTEN 0 4096 100.122.168.47:443 0.0.0.0:* users:(("caddy",pid=7,fd=4))',
                interfaces,
            ),
        ]

        groups = module["group_listeners"](listeners)

        self.assertEqual(groups[0].exposure, "wildcard")

    def test_formats_scoped_ipv6_bind_without_repeating_interface(self):
        module = self.load_module()
        interfaces = self.interface_index(module)
        listener = module["parse_ss_line"](
            'tcp LISTEN 0 4096 [fe80::d3f0:5af1:36b9:67c]%enp5s0:45100 0.0.0.0:* users:(("svc",pid=9,fd=3))',
            interfaces,
        )

        self.assertEqual(listener.bind_label, "[fe80::d3f0:5af1:36b9:67c%enp5s0]:45100")

    def test_lan_rows_show_only_lan_binds_for_mixed_services(self):
        module = self.load_module()
        interfaces = self.interface_index(module)
        listeners = [
            module["parse_ss_line"](
                'tcp LISTEN 0 4096 172.16.0.208%enp5s0:45100 0.0.0.0:* users:(("svc",pid=9,fd=3))',
                interfaces,
            ),
            module["parse_ss_line"](
                'tcp LISTEN 0 4096 100.122.168.47%tailscale0:45100 0.0.0.0:* users:(("svc",pid=9,fd=4))',
                interfaces,
            ),
            module["parse_ss_line"](
                'tcp LISTEN 0 4096 172.18.0.1%br-test:45100 0.0.0.0:* users:(("svc",pid=9,fd=5))',
                interfaces,
            ),
        ]
        groups = module["group_listeners"](listeners)

        rows = module["section_rows"](groups, "lan")

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].binds, "172.16.0.208%enp5s0:45100")
        self.assertEqual(rows[0].notes, "also bridge=1, tailscale=1")

    def test_collapses_consecutive_port_ranges_with_different_pids(self):
        module = self.load_module()
        interfaces = self.interface_index(module)
        listeners = []
        for port in range(3000, 3005):
            listeners.extend(
                [
                    module["parse_ss_line"](
                        f'tcp LISTEN 0 4096 0.0.0.0:{port} 0.0.0.0:* users:(("docker-proxy",pid={port},fd=3))',
                        interfaces,
                    ),
                    module["parse_ss_line"](
                        f'tcp LISTEN 0 4096 [::]:{port} [::]:* users:(("docker-proxy",pid={port + 100},fd=3))',
                        interfaces,
                    ),
                ]
            )
        groups = module["group_listeners"](listeners)

        rows = module["section_rows"](groups, "wildcard")

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].port, "3000-3004")
        self.assertEqual(rows[0].process, "docker-proxy")
        self.assertEqual(rows[0].binds, "0.0.0.0:3000-3004, [::]:3000-3004")

    def test_process_display_rows_collapse_same_process_name(self):
        module = self.load_module()
        interfaces = self.interface_index(module)
        listeners = []
        for port in range(3000, 3005):
            listeners.append(
                module["parse_ss_line"](
                    f'tcp LISTEN 0 4096 0.0.0.0:{port} 0.0.0.0:* users:(("docker-proxy",pid={port},fd=3))',
                    interfaces,
                )
            )
        for port in range(5000, 5005):
            listeners.append(
                module["parse_ss_line"](
                    f'tcp LISTEN 0 4096 0.0.0.0:{port} 0.0.0.0:* users:(("docker-proxy",pid={port},fd=3))',
                    interfaces,
                )
            )
        groups = module["group_listeners"](listeners)
        rows = module["section_rows"](groups, "wildcard")

        display_rows = module["process_display_rows"](rows)

        self.assertEqual(len(display_rows), 1)
        self.assertEqual(display_rows[0].process, "docker-proxy")
        self.assertEqual(display_rows[0].listeners, "tcp:3000-3004, tcp:5000-5004")

    def test_process_display_rows_do_not_collapse_unknown_processes(self):
        module = self.load_module()
        interfaces = self.interface_index(module)
        listeners = [
            module["parse_ss_line"](
                "tcp LISTEN 0 4096 0.0.0.0:22 0.0.0.0:*",
                interfaces,
            ),
            module["parse_ss_line"](
                "tcp LISTEN 0 4096 0.0.0.0:23 0.0.0.0:*",
                interfaces,
            ),
        ]
        groups = module["group_listeners"](listeners)
        rows = module["section_rows"](groups, "wildcard")

        display_rows = module["process_display_rows"](rows)

        self.assertEqual(len(display_rows), 2)
        self.assertEqual([row.process for row in display_rows], ["-", "-"])

    def test_table_wraps_long_bind_cells(self):
        module = self.load_module()
        rows = [
            [
                "tcp",
                "1234",
                "svc[9]",
                ", ".join(f"192.0.2.{index}:1234" for index in range(20)),
                "",
            ]
        ]

        lines = module["format_table"](["Proto", "Port", "Process", "Binds", "Notes"], rows)

        self.assertLessEqual(max(len(line) for line in lines), 132)
        self.assertGreater(len(lines), 3)


if __name__ == "__main__":
    unittest.main()
