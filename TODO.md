- [ ] remove all "requires more effort to fix" from zizmor
- [ ] setup trusted publishing with PyPI
  - [ ] reenable snapshot publishing step
- [ ] replace Artifactory tokens with ones from the team
- [x] make repo compliant
- [ ] update status checks in branch protection rules
- [ ] add `__repr__` function after code is freshly moved + `_NamedPartial` + `NoDefault`

```py
@dataclass
class CredentialsValue:
    name: str
    vcap_key: Optional[Tuple[str, ...]] = None
    transform_fn: Optional[Callable] = None

    def __repr__(self):
        fn = self.transform_fn.__name__ if self.transform_fn else None
        return f"CredentialsValue(name={self.name!r}, vcap_key={self.vcap_key!r}, transform_fn={fn})"
```

after os-migration PR is merged:

- [ ] create initial version tags (and delete old incorrect ones)
- [ ] use setup action from main not os-migration
